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

#define mt make_tuple
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

char string_in_buffer[(int)260];


void fast_scan(int &x) { scanf("%d", &x); }
void fast_scan(long long &x) { scanf("%lld", &x); }
void fast_scan(unsigned long long &x) { scanf("%llu", &x); }
void fast_scan(double &x) { scanf("%lf", &x); }
void fast_scan(long double &x) { scanf("%Lf", &x); }
void fast_scan(char &x) { 
	scanf("%c", &x); 
	if (x == '\n') {
		fast_scan(x);
	}
}
void fast_scan(string &x) {
	scanf("%s", string_in_buffer);
	x = string(string_in_buffer);
}

template<class TFirst, class TSecond>
void fast_scan(pair<TFirst, TSecond> &p) {
	fast_scan(p.first);
	fast_scan(p.second);
}

template <class T>
void fast_scan(vector<T> &v) {
	for (auto &x : v) fast_scan(x);
}

void fast_print(const int &x) { printf("%d", x); }
void fast_print(const long long &x) { printf("%lld", x); }
void fast_print(const unsigned long long &x) { printf("%llu", x); }
void fast_print(const double &x) { printf("%.15lf", x); }
void fast_print(const long double &x) { printf("%.15Lf", x); }
void fast_print(const char &x) { printf("%c", x); };
void fast_print(const string &x) { printf("%s", x.c_str());}

template<class TFirst, class TSecond>
void fast_print(const pair<TFirst, TSecond> &p) {
	fast_print(p.first);
	fast_print(' ');
	fast_print(p.second);
}

template <class T>
void fast_print(const vector<T> &v) {
	if (v.empty()) return;
	fast_print(v[0]);
	for (int i = 1; i < v.size(); i++) {
		fast_print(" ");
		fast_print(v[i]);
	}
}

template <class T>
void fast_print(const vector<vector<T>> &v) {
	if (v.empty()) return;
	fast_print(v[0]);
	for (int i = 1; i < v.size(); i++) {
		fast_print("\n");
		fast_print(v[i]);
	}
}



using namespace std;


namespace smart_io {
	string print_start = "";
	string sep = " ";
	bool first_print = false;

	void precall_print() {
		fast_print(print_start);
		print_start = "\n";
		first_print = true;
	}
} //namespace smart_io


template <class T>
ostream &operator,(ostream &os, const T &object) {
	if (!smart_io::first_print) {
		fast_print(smart_io::sep);
	} else {
		smart_io::first_print = false;
	}
	fast_print(object);
	return os;
}

template <class T>
istream &operator,(istream &is, T &object) {
	fast_scan(object);
	return is;
}

namespace typedefs {
	typedef long long ll;
	typedef unsigned long long ull;
	typedef vector<int> vi;
	typedef pair<int, int> pii;
	typedef vector<vector<pair<int, int>>> vvpii;
	typedef vector<vector<pair<bool, int>>> vvpbi;
}

using namespace typedefs;

#define print    \
smart_io::precall_print(); \
cout,

#define scan cin,


namespace TreeSegment {
	typedef int value_type;
	typedef struct {int plus_mod;} Mod;
	
	value_type magic(const value_type &a, const value_type &b) {
		return a + b;
	}

	Mod merge_mods(const Mod &a, const Mod &b) {
		Mod mod;
		mod.plus_mod = a.plus_mod + b.plus_mod;
		return mod;
	}

	value_type apply_mod(int left, int right, const value_type &value, const Mod &mod) {
		return value + (mod.plus_mod * (right - left));
	}



	class Node {
	public:
		value_type value;
		Node *left_child = NULL, *right_child = NULL;
		bool pushed = true;

		Mod mod;

		int ths_left, ths_right;

		int length() { return ths_right - ths_left; };

		bool intersect(int left, int right) {
			return !(ths_right <= left || right <= ths_left);
		}

		bool is_list() {
			return (!left_child) && (!right_child);
		}

		void push() {
			//TODO!
			if (pushed) return;

			if (is_list()) {
				value = apply_mod(ths_left, ths_right, value, mod);
				pushed = true;
				return;
			}

			if (left_child) {
				if (left_child->pushed) {
					left_child->mod = mod;
				} else {
					left_child->mod = merge_mods(left_child->mod, mod);
				}
				left_child->pushed = false;
			}

			if (right_child) {
				if (right_child->pushed) {
					right_child->mod = mod;
				} else {
					right_child->mod = merge_mods(right_child->mod, mod);
				}
				right_child->pushed = false;
			}

			pushed = true;
			recalc();
		}

		void recalc() {
			// assert(mod.plus_mod == 0);
			if (is_list()) {
				assert(pushed);
				return;
			}
			assert(left_child && right_child);

			value_type vleft;
			if (left_child->pushed) {
				vleft = left_child->value;
			} else {
				vleft = apply_mod(left_child->ths_left, left_child->ths_right, left_child->value, left_child->mod);
			}

			value_type vright;
			if (right_child->pushed) {
				vright = right_child->value;
			} else {
				vright = apply_mod(right_child->ths_left, right_child->ths_right, right_child->value, right_child->mod);
			}

			value = magic(vleft, vright);
		}

		Node() {}
		
		Node(int left, int right, const vector<value_type> &arr) {
			ths_left = left;
			ths_right = right;
			if (left == right - 1) {
				value = arr[left];
			} else {
				int mid = (right + left) / 2;

				left_child = new Node(left, mid, arr);
				right_child = new Node(mid, right, arr);
			}
			recalc();
		}

		value_type query(int qleft, int qright) {
			assert(this);
			assert(!(ths_right <= qleft || qright <= ths_left));
			push();
			// if full include
			if (qleft <= ths_left && ths_right <= qright) {
				return value;
			}

			if (left_child && left_child->intersect(qleft, qright)) {
				if (right_child && right_child->intersect(qleft, qright)) {
					return magic(left_child->query(qleft, qright)
								, right_child->query(qleft, qright));
				} else {
					return left_child->query(qleft, qright);
				}
			} else {
				return right_child->query(qleft, qright);
			}
		}

		void replace(int ind, value_type d) {
			assert(this);
			push();
			// if full include
			if (is_list() && ths_left <= ind && ind < ths_right) {
				value = d;
				return;
			}

			if (left_child && left_child->intersect(ind, ind + 1)) {
				left_child->replace(ind, d);
			}
			
			if (right_child && right_child->intersect(ind, ind + 1)) {
				right_child->replace(ind, d);
			}
			recalc();
		}

		void update(int qleft, int qright, Mod pmod) {
			assert(this);
			assert(!(ths_right <= qleft || qright <= ths_left));
			push();
			// if full include
			if (qleft <= ths_left && ths_right <= qright) {
				if (pushed) {
					mod = pmod;
				} else {
					mod = merge_mods(mod, pmod);
				}
				pushed = false;
				push();
			} else {
				if (left_child && left_child->intersect(qleft, qright)) {
					left_child->update(qleft, qright, pmod);
				}

				if (right_child && right_child->intersect(qleft, qright)) {
					right_child->update(qleft, qright, pmod);
				}
			}
			recalc();
		}
	};
};




int main(int argc, char *argv[]) {

	int n;
	scan n;
	n += 20;
	int m;
	scan m;
	vector<int> v(n, 0);
	TreeSegment::Node *node = new TreeSegment::Node(0, n, v);
	for (int i = 0; i < m; i++) {
		char q;
		scan q;
		if (q == '2') {
			int l, r;
			scan l, r;
			// r++;
			print node->query(l, r);
			smart_io::print_start = " ";
		} else {
			int l, r, d;
			scan l, r, d;
			// r++;
			node->update(l, r, {d});
		}
	}
}