#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <map>
#include <set>
#include <queue>
#include <ostream>
#include <istream>
#include <typeinfo>
#include <iomanip>
#include <cstdio>
#include <cstdlib>
#include <cassert>
#include <limits>
#include <fstream>
#include <array>
#include <list>
#include <functional>


#define print cout,
#define scan cin,
#define x first
#define y second
#define pb push_back
#define ppb pop_back
#define pf push_front
#define ppf pop_front
#define mp make_pair
#define umap unordered_map
#define uset unordered_set
#define rt return 0;
#define elif else if
#define len(v) ((int)v.size())


using namespace std;

// I/O Stream Manager
namespace Smart_IO_Stream {

	template <class T_First, class T_Second>
	ostream& operator<<(ostream& os, const pair<T_First, T_Second> &p) {
		os << p.first << " " << p.second;
		return os;
	}

	template <class T>
	ostream& operator<<(ostream& os, const vector<T> &v) {
		if (v.empty()) return os;
		for (int i = 0; i < len(v) - 1; i++) {
			os << v[i] << " ";
		}
		os << v[len(v) - 1];
		return os;
	}

	template <class T>
	ostream& operator<<(ostream& os, const vector<vector<T>> &v) {
		if (v.empty()) return os;
		for (int i = 0; i < len(v) - 1; i++) {
			os << v[i];
			os << endl;
		}
		os << v[len(v) - 1];
		return os;
	}


	template <class T_First, class T_Second>
	istream& operator>>(istream& is, pair<T_First, T_Second> &p) {
		is >> p.first >> p.second;
		return is;
	}

	template <class T>
	istream& operator>>(istream& is, vector<T> &v) {
		for (auto &x : v) {
			is >> x;
		}
		return is;
	}

	template<class T>
	istream &operator,(istream &is, T &obj) {
		is >> obj;
		return is;
	}

	template<class T>
	ostream &operator,(ostream &os, const T &obj) {
		return (os << obj << " ");
	}
	

	enum OutSymb {
		nl, ptr, ptr2, cma, 
	};

	ostream &operator,(ostream &os, OutSymb s) {
		switch (s) {
			case nl:
				os << endl;
				break;
			case ptr:
				os << "-> ";
				break;
			case ptr2:
				os << "--> ";
				break;
			case cma:
				os << ", ";
				break;
			default:
				break;
		}
		return os;
	}
}// namespace Smart_IO_Stream


void set_accuracy(int accure) {
	cout << setprecision(accure) << fixed;
}

namespace defython {
	// vector<xrange> xrange::xranges = vector<xrange>();
	template <class T, class T_Rez>
	T_Rez sum(vector<T> &v) {
		T_Rez rez = (T_Rez)0;
		for (auto &x : v) {
			rez += x;
		}
		return rez;
	}

	template <class T>
	long long sum(vector<T> &v) {
		return sum<T, long long>(v);
	}

	template <class T>
	T max(vector<T> &v) {
		if (v.empty())
			assert(false);
		T assume_max = v[0];
		for (auto &x : v) {
			if (assume_max < x) {
				assume_max = x;
			}
		}
		return assume_max;
	}

	template <class T>
	T min(vector<T> &v) {
		if (v.empty())
			assert(false);
		T assume_min = v[0];
		for (auto &x : v) {
			if (assume_min > x) {
				assume_min = x;
			}
		}
		return assume_min;
	}

	template<class T_Map, class T_Key, class T_Value>
	T_Value get(const T_Map &m, const T_Key &key, const T_Value &default_value) {
		auto x = m.find(key);
		if (x == m.end())
			return default_value;
		return x->second;
	}

}// namespace defython

namespace typedefs {
	typedef long long ll;
	typedef unsigned long long ull;
	typedef vector<int> vi;
	typedef pair<int, int> pii;
	typedef vector<vector<pair<int, int>>> vvpii;
	typedef vector<vector<pair<bool, int>>> vvpbi;
}

using namespace Smart_IO_Stream;
using namespace typedefs;
using namespace defython;



ll MOD = 1000000000 + 7;
ll MOD2 = 1000000 + 7;
ll max_p = 31;


vector<ll> power(250);

ll get_substr_hash(vector<ll> &h, int i, int j) {
	ll hash = h[j];
	if (i > 0) {
		hash -= (h[i - 1] * power[j - i + 1]) % MOD;
	}
	return hash;
}


bool is_equal(vector<ll> &h1, vector<ll> &h2, int i, int j, int len) {
	int l1 = i, r1 = i + len - 1, l2 = j, r2 = j + len - 1;
	ll hash1 = h1[r1];
	if (l1 > 0) {
		hash1 -= (h1[l1 - 1] * power[r1 - l1 + 1]) % MOD;
	}
	ll hash2 = h2[r2];
	if (l2 > 0) {
		hash2 -= (h2[l2 - 1] * power[r2 - l2 + 1]) % MOD;
	}
	if (hash1 < 0) {
		hash1 = MOD - (abs(hash1) % MOD);
	}
	if (hash2 < 0) {
		hash2 = MOD - (abs(hash2) % MOD);
	}
	hash1 %= MOD;
	hash2 %= MOD;
	return hash1 == hash2;
}

int get_number(char c) {
	return c - 'a' + 1;
}


vector<ll> get_hash(string &s) {
	int n = s.length();
	vector<ll> hash(n);
	hash[0] = get_number(s[0]);
	for (int i = 1; i < n; i++) {
		hash[i] = ((hash[i - 1] * max_p) % MOD) + get_number(s[i]);
		hash[i] %= MOD;
	}
	return hash;
}


vector<int> prefix_func(const string &s) {
	int n = len(s);
	vector<int> rez(n);
	rez[0] = 0;
	for (int i = 1; i < n; i++) {
		int j = rez[i - 1];
		while (j > 0 && s[j] != s[i]) {
			j = rez[j - 1];
		}
		if (s[j] == s[i]) {
			rez[i] = j + 1;
		} else {
			rez[i] = 0;
		}
	}
	return rez;
}

int main(int argc, char *argv[]) {
	{
		bool is_debug = false;
		if (argc > 1 && string(argv[1]) == "-debug") {
			is_debug = true;
		}
		if (!is_debug) {
			freopen("period.in", "r", stdin);
			freopen("period.out", "w", stdout);
		}
	}
	string s;
	cin >> s;
	vector<int> v = prefix_func(s);
	// print v, nl;
	int iter = len(s) - 2;
	if (v[len(s) - 1] == 0) {
		iter = len(s) - 1;
	} else {
		while (v[iter] != 0 && v[iter] + 1 == v[iter + 1]) {
			iter--;
		}
	}
	iter++;
	// print iter;
	if (len(s) % iter == 0) {
		print len(s) / iter;
	} else {
		print 1;
	}
}