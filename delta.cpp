// delta.cpp
// vector + inverse après o selon f
// pur c++ propre

#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using std::vector;
using std::string;
using std::cout;

struct Delta {
    vector<string> plus;
    vector<string> moins;
};

// rasoir o: garde le plus court
vector<string> razor(const vector<string>& items, int depth = 0) {
    if (depth > 5 || items.size() <= 3) {
        return items;
    }

    vector<string> result;
    vector<bool> skip(items.size(), false);

    for (size_t i = 0; i < items.size(); ++i) {
        if (skip[i]) continue;

        bool merged = false;
        for (size_t j = i + 1; j < items.size(); ++j) {
            if (skip[j]) continue;

            int diff = static_cast<int>(items[i].length()) -
                       static_cast<int>(items[j].length());
            if (diff >= -2 && diff <= 2) {
                result.push_back(items[i].length() <= items[j].length()
                                 ? items[i] : items[j]);
                skip[i] = skip[j] = true;
                merged = true;
                break;
            }
        }
        if (!merged && !skip[i]) {
            result.push_back(items[i]);
        }
    }

    if (result != items) {
        return razor(result, depth + 1);
    }
    return items;
}

// boucle f: itère jusqu'à stable
Delta loop(Delta d, int generations = 3) {
    for (int g = 0; g < generations; ++g) {
        d.plus = razor(d.plus);
        d.moins = razor(d.moins);

        vector<string> new_plus;
        vector<string> new_moins;

        for (const auto& p : d.plus) {
            if (p.length() <= 6) new_plus.push_back(p);
        }
        for (const auto& m : d.moins) {
            if (m.length() <= 6) new_moins.push_back(m);
        }

        if (new_plus == d.plus && new_moins == d.moins) {
            break;
        }
        d.plus = new_plus;
        d.moins = new_moins;
    }
    return d;
}

// inverse
Delta inverse(const Delta& d) {
    return {d.moins, d.plus};
}

void print(const vector<string>& v) {
    cout << "[";
    for (size_t i = 0; i < v.size(); ++i) {
        cout << v[i];
        if (i < v.size() - 1) cout << ", ";
    }
    cout << "]";
}

int main() {
    Delta d;
    d.plus = {"sens", "local", "psy", "Q", "sacre", "organes", "o", "f", "flow", "muse"};
    d.moins = {"api", "rigide", "mort"};

    cout << "=== raw ===" << "\n";
    cout << "+ "; print(d.plus); cout << "\n";
    cout << "- "; print(d.moins); cout << "\n";

    cout << "\n=== o recursif ===" << "\n";
    auto r = d;
    r.plus = razor(d.plus);
    r.moins = razor(d.moins);
    cout << "+ "; print(r.plus); cout << "\n";
    cout << "- "; print(r.moins); cout << "\n";

    cout << "\n=== f loop ===" << "\n";
    auto f = loop(d);
    cout << "+ "; print(f.plus); cout << "\n";
    cout << "- "; print(f.moins); cout << "\n";

    cout << "\n=== inverse ===" << "\n";
    auto inv = inverse(f);
    cout << "+ "; print(inv.plus); cout << "\n";
    cout << "- "; print(inv.moins); cout << "\n";

    cout << "\n=== stable ===" << "\n";
    cout << "D  = +creation -destruction" << "\n";
    cout << "V  = +destruction -creation" << "\n";
    cout << "DV = 0" << "\n";

    return 0;
}
