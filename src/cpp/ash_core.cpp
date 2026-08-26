/**
 * ASH C++ - Analyseur spectral à géométrie harmonique
 * Version optimisée (équivalente à ash_optimized.py)
 * Compilation : g++ -std=c++17 -O2 ash_core.cpp -o ash_core
 * Utilisation : ./ash_core fichier.csv [type_signal]
 *   type_signal : eeg, ecg, vibration, generic (defaut generic)
 * Auteur : Patrice Portemann
 * Date : 2026-06-07
 *
 * Note C12.1 : implémentation de référence portable (FFT radix-2 interne,
 * aucune dépendance externe). La référence canonique reste
 * src/python/ash_core.py ; les deux implémentations partagent la même
 * grille f_n = f0 * 2^(n/12) et les mêmes invariants (Rc, Rtop, Rdyn, ReN).
 */

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <complex>
#include <iomanip>

using namespace std;

// -------------------------------------------------------------
// FFT radix-2 (taille 256)
// -------------------------------------------------------------
using Complex = complex<double>;

void fft(vector<Complex>& a, bool invert) {
    int n = a.size();
    if (n <= 1) return;
    // réarrangement bit-reversal
    for (int i = 1, j = 0; i < n; i++) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1)
            j ^= bit;
        j ^= bit;
        if (i < j) swap(a[i], a[j]);
    }
    for (int len = 2; len <= n; len <<= 1) {
        double ang = 2 * M_PI / len * (invert ? -1 : 1);
        Complex wlen(cos(ang), sin(ang));
        for (int i = 0; i < n; i += len) {
            Complex w(1);
            for (int j = 0; j < len / 2; j++) {
                Complex u = a[i + j];
                Complex v = a[i + j + len / 2] * w;
                a[i + j] = u + v;
                a[i + j + len / 2] = u - v;
                w *= wlen;
            }
        }
    }
    if (invert) {
        for (Complex& x : a)
            x /= n;
    }
}

void hanning(vector<double>& win) {
    int n = win.size();
    for (int i = 0; i < n; ++i)
        win[i] = 0.5 * (1 - cos(2 * M_PI * i / (n - 1)));
}

// -------------------------------------------------------------
// Lecture d'un fichier CSV (une colonne numérique, optionnellement une colonne time)
// -------------------------------------------------------------
vector<double> read_signal(const string& filename, double& fs_est) {
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Erreur: impossible d'ouvrir " << filename << endl;
        return {};
    }
    string line;
    vector<double> signal;
    vector<double> times;
    bool has_time = false;
    while (getline(file, line)) {
        stringstream ss(line);
        string cell;
        double t = 0.0, val = 0.0;
        int col = 0;
        bool first_num = true;
        while (getline(ss, cell, ',')) {
            char* end;
            double d = strtod(cell.c_str(), &end);
            if (end != cell.c_str()) { // c'est un nombre
                if (first_num) {
                    if (col == 0) {
                        // première colonne numérique, on suppose que c'est le temps si le nom est 'time' ou la première colonne
                        // Pour simplifier, on stocke les deux colonnes si possible
                        t = d;
                        has_time = true;
                    } else if (col == 1) {
                        val = d;
                        break;
                    }
                    first_num = false;
                }
            }
            col++;
        }
        if (!first_num) {
            if (has_time) {
                times.push_back(t);
                signal.push_back(val);
            } else {
                signal.push_back(t);
            }
        }
    }
    if (times.size() >= 2) {
        double dt = times[1] - times[0];
        fs_est = 1.0 / dt;
        cout << "Fs estimée à partir de la colonne temps : " << fs_est << " Hz" << endl;
    } else {
        fs_est = 250.0; // valeur par défaut
    }
    return signal;
}

// -------------------------------------------------------------
// Classe ASH
// -------------------------------------------------------------
class ASH {
public:
    struct Result {
        double time;
        double Rc;
        int Rtop;
        double Rdyn;
        vector<double> bands;      // taille 7
        double ReN;
        string regime;
    };

    ASH(double fs, const string& signal_type = "generic",
        double f0 = -1.0, int n_octaves = -1, double window_duration = -1.0, double overlap = 0.5)
        : fs_(fs), overlap_(overlap) {
        // Paramètres par défaut selon le type de signal
        if (signal_type == "eeg") {
            if (f0 < 0) f0 = 1.0;
            if (n_octaves < 0) n_octaves = 4;
            if (window_duration < 0) window_duration = 2.0;
        } else if (signal_type == "ecg") {
            if (f0 < 0) f0 = 1.0;
            if (n_octaves < 0) n_octaves = 4;
            if (window_duration < 0) window_duration = 2.0;
        } else if (signal_type == "vibration") {
            if (f0 < 0) f0 = 10.0;
            if (n_octaves < 0) n_octaves = 5;
            if (window_duration < 0) window_duration = 1.0;
        } else { // generic
            if (f0 < 0) f0 = 1.0;
            if (n_octaves < 0) n_octaves = 4;
            if (window_duration < 0) window_duration = 2.0;
        }
        f0_ = f0;
        n_octaves_ = n_octaves;
        window_duration_ = window_duration;
        window_size_ = int(fs_ * window_duration_);
        if (window_size_ < 64) window_size_ = 64;
        if (window_size_ > 1024) window_size_ = 1024;
        hop_ = int(window_size_ * (1 - overlap_));
        n_notes_ = n_octaves_ * 12;
        build_grid();
        nfft_ = 256; // taille fixe pour FFT (puissance de 2)
    }

    vector<Result> process_signal(const vector<double>& signal) {
        vector<Result> results;
        int n_windows = (signal.size() - window_size_) / hop_ + 1;
        if (n_windows <= 0) {
            cerr << "Signal trop court pour la fenêtre choisie." << endl;
            return results;
        }
        for (int i = 0; i < n_windows; ++i) {
            int start = i * hop_;
            vector<double> seg(signal.begin() + start, signal.begin() + start + window_size_);
            double t_center = (start + window_size_ / 2.0) / fs_;
            Result res = process_window(seg, t_center);
            results.push_back(res);
        }
        return results;
    }

private:
    double fs_, f0_, overlap_, window_duration_;
    int n_octaves_, n_notes_, window_size_, hop_, nfft_;
    vector<double> freqs_noetic_;

    void build_grid() {
        freqs_noetic_.resize(n_notes_);
        for (int i = 0; i < n_notes_; ++i) {
            freqs_noetic_[i] = f0_ * pow(2.0, (double)i / 12.0);
        }
    }

    vector<double> spectral_projection(const vector<double>& signal) {
        // FFT de la fenêtre (taille nfft_)
        int n = min(nfft_, (int)signal.size());
        vector<Complex> x(n);
        for (int i = 0; i < n; ++i) x[i] = signal[i];
        // fenêtre de Hanning
        vector<double> win(n);
        hanning(win);
        for (int i = 0; i < n; ++i) x[i] *= win[i];
        fft(x, false);
        // module
        vector<double> mag(n / 2);
        for (int i = 0; i < n / 2; ++i) {
            mag[i] = abs(x[i]) / n;
        }
        // interpolation aux fréquences noétiques
        vector<double> coeffs(n_notes_, 0.0);
        for (int i = 0; i < n_notes_; ++i) {
            double f = freqs_noetic_[i];
            int bin = (int)(f * n / fs_);
            if (bin >= 0 && bin < (int)mag.size()) {
                coeffs[i] = mag[bin];
            } else {
                coeffs[i] = 0.0;
            }
        }
        return coeffs;
    }

    void compute_residues(const vector<double>& coeffs, double& Rc, int& Rtop, double& Rdyn) {
        Rc = accumulate(coeffs.begin(), coeffs.end(), 0.0);
        if (Rc < 1e-12) {
            Rtop = 0;
            Rdyn = 1.0;
            return;
        }
        // détection de pics
        vector<int> peaks;
        double max_coeff = *max_element(coeffs.begin(), coeffs.end());
        double thresh = 0.1 * max_coeff;
        for (int i = 1; i < (int)coeffs.size() - 1; ++i) {
            if (coeffs[i] > coeffs[i-1] && coeffs[i] > coeffs[i+1] && coeffs[i] > thresh) {
                peaks.push_back(i);
            }
        }
        Rtop = peaks.size();
        if (Rtop >= 2) {
            vector<double> log_ratios;
            for (size_t k = 0; k < peaks.size()-1; ++k) {
                double ratio = freqs_noetic_[peaks[k+1]] / freqs_noetic_[peaks[k]];
                log_ratios.push_back(log(ratio));
            }
            double mean = accumulate(log_ratios.begin(), log_ratios.end(), 0.0) / log_ratios.size();
            double var = 0.0;
            for (double lr : log_ratios) var += (lr - mean) * (lr - mean);
            double stddev = sqrt(var / log_ratios.size());
            Rdyn = stddev / (mean + 1e-8);
        } else {
            Rdyn = 1.0;
        }
    }

    vector<double> project_bands(const vector<double>& coeffs) {
        vector<double> bands(7, 0.0);
        for (int oct = 0; oct < min(n_octaves_, 7); ++oct) {
            int start = oct * 12;
            double sum = 0.0;
            for (int i = 0; i < 12; ++i) {
                if (start + i < (int)coeffs.size()) sum += coeffs[start + i];
            }
            bands[oct] = sum;
        }
        double norm = sqrt(inner_product(bands.begin(), bands.end(), bands.begin(), 0.0));
        if (norm > 1e-8) {
            for (double& b : bands) b /= norm;
        }
        return bands;
    }

    void compute_ren(double Rc, int Rtop, double Rdyn, const vector<double>& bands,
                     double& ReN, string& regime) {
        double total = accumulate(bands.begin(), bands.end(), 0.0);
        if (total < 1e-12) {
            ReN = 0.0;
            regime = "indéfini";
            return;
        }
        vector<double> p(7);
        for (int i = 0; i < 7; ++i) p[i] = bands[i] / total;
        double entropy = 0.0;
        for (int i = 0; i < 7; ++i) {
            if (p[i] > 0) entropy -= p[i] * log(p[i]);
        }
        vector<double> sorted_bands = bands;
        sort(sorted_bands.begin(), sorted_bands.end(), greater<double>());
        double dominance = sorted_bands[0] - sorted_bands[1];
        double torsion = Rtop * dominance;
        double pressure = Rc * (entropy + 1e-8);
        ReN = ((Rdyn + 1e-6) * torsion) / (pressure + 1e-8) * 100.0;
        if (ReN > 10.0) regime = "Quantique (torsion dominante)";
        else if (ReN < 1.0) regime = "Cosmologique (pression dominante)";
        else regime = "Méso (industriel / transition)";
    }

    Result process_window(const vector<double>& seg, double t_center) {
        vector<double> coeffs = spectral_projection(seg);
        double Rc, Rdyn;
        int Rtop;
        compute_residues(coeffs, Rc, Rtop, Rdyn);
        vector<double> bands = project_bands(coeffs);
        double ReN;
        string regime;
        compute_ren(Rc, Rtop, Rdyn, bands, ReN, regime);
        return {t_center, Rc, Rtop, Rdyn, bands, ReN, regime};
    }
};

// -------------------------------------------------------------
// Fonction principale
// -------------------------------------------------------------
int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage: " << argv[0] << " fichier.csv [type_signal]" << endl;
        cerr << "   type_signal : eeg, ecg, vibration, generic (defaut generic)" << endl;
        return 1;
    }
    string filename = argv[1];
    string signal_type = (argc > 2) ? argv[2] : "generic";

    double fs_est = 250.0;
    vector<double> signal = read_signal(filename, fs_est);
    if (signal.empty()) {
        cerr << "Aucun signal trouvé." << endl;
        return 1;
    }
    cout << "Signal : " << signal.size() << " échantillons, fs=" << fs_est << " Hz" << endl;

    ASH ash(fs_est, signal_type);
    auto results = ash.process_signal(signal);

    // Affichage des résultats (premières lignes)
    cout << fixed << setprecision(6);
    cout << "\n=== Résultats ASH ===\n";
    cout << "time\tRc\tRtop\tRdyn\tReN\tregime\n";
    for (size_t i = 0; i < results.size() && i < 10; ++i) {
        cout << results[i].time << "\t"
             << results[i].Rc << "\t"
             << results[i].Rtop << "\t"
             << results[i].Rdyn << "\t"
             << results[i].ReN << "\t"
             << results[i].regime << "\n";
    }

    // Moyennes
    double Rc_sum = 0.0, Rdyn_sum = 0.0, ReN_sum = 0.0;
    int Rtop_sum = 0;
    for (const auto& r : results) {
        Rc_sum += r.Rc;
        Rtop_sum += r.Rtop;
        Rdyn_sum += r.Rdyn;
        ReN_sum += r.ReN;
    }
    int n = results.size();
    cout << "\n=== Résumé ===\n";
    cout << "Rc moyen   = " << Rc_sum / n << endl;
    cout << "Rtop moyen = " << (double)Rtop_sum / n << endl;
    cout << "Rdyn moyen = " << Rdyn_sum / n << endl;
    cout << "ReN moyen  = " << ReN_sum / n << endl;

    // Sauvegarde dans ash_results.csv
    ofstream out("ash_results_cpp.csv");
    if (out.is_open()) {
        out << "time,Rc,Rtop,Rdyn,ReN,regime\n";
        for (const auto& r : results) {
            out << r.time << "," << r.Rc << "," << r.Rtop << "," << r.Rdyn << "," << r.ReN << "," << r.regime << "\n";
        }
        out.close();
        cout << "Résultats sauvegardés dans ash_results_cpp.csv" << endl;
    }

    return 0;
}
