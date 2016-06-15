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


double M_PI = 3.141592653589793;


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
void fast_print(const double &x) { printf("%lf", x); }
void fast_print(const long double &x) { printf("%10.7Lf", x); }
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
}


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


const double EPS = 0.0000001;


double to_radians(double ang_deg) {
	return (ang_deg * M_PI / 180.0);
}

double to_degrees(double ang_rad) {
	return (ang_rad * 180.0 / M_PI);
}

bool eq(double a, double b=0) {
	return abs(a - b) <= EPS;
}


class point {
public:
	double x, y;
	
	inline point() {}

	inline point(double _x, double _y):x(_x), y(_y) {}
	
	void set_polar(double _angle, double _dist) {
		x = cos(_angle) * _dist;
		y = sin(_angle) * _dist;
	}

	double length() {
		return sqrt(x * x + y * y);
	}

	double angle() {
		return atan2(y, x);
	}

	friend istream &operator>>(istream &is, point &p) {
		is >> p.x >> p.y;
		return is;
	}

	friend point operator-(point p1, point p2) {
		return point(p1.x - p2.x, p1.y - p2.y);
	}

	void operator-=(const point &p) {
		x -= p.x;
		y -= p.y;
	}

	point operator/(double d) {
		return point(x / d, y / d);
	}

	point operator*(double d) {
		return point(x * d, y * d);
	}

	void operator/=(double d) {
		x /= d;
		y /= d;
	}

	void operator*=(double d) {
		x *= d;
		y *= d;
	}

	point rotate90() {
		return point(-y, x);
	}

	point invert() {
		return point(-x, -y);
	}

	void set_length(double l) {
		double cur_len = length();
		x /= cur_len;
		y /= cur_len;
		x *= l;
		y *= l;
	}

	double operator*(const point &p) {
		return (x * p.x + y * p.y);
	}

	double operator^(point &p) {
		return (x * p.y - y * p.x);
	}

	point operator+(point p) {
		return point(x + p.x, y + p.y);
	}

	void operator+=(point p) {
		x += p.x;
		y += p.y;
	}
	
	friend ostream &operator<<(ostream &os, const point &p) {
		os << p.x << " " << p.y;
		return os;
	}

	bool operator==(point p) {
		return eq(x, p.x) && eq(y, p.y);
	}

	bool operator<(const point &p) const {
		return vector<double>{x, y} < vector<double>{p.x, p.y};
	}

	double angle_to(point p) {
		return acos(((*this) * p) / (p.length() * length()));
	}
};

bool in(point a) {
	if (a.y < 0) return 0;
	if (a.y > 0) return 1;
	return a.x > 0;
}

int main(int argc, char *argv[]) {
	int n;
	scanf("%d", &n);
	vector<point> v(n);
	for (int i = 0; i < n; i++) {
		scanf("%lf %lf", &(v[i].x), &(v[i].y));
	}

	sort(v.begin(), v.end(), [](point a, point b){
		bool f1 = in(a);
		bool f2 = in(b);
		if (f1 == f2) {
			double x = a ^ b;
			if (x == 0) {
				return a.length() < b.length();
			} else {
				return x > 0;
			}
		}
		if (f1) {
			return true;
		}
		return false;
	});

	double mx = 0;

	for (int i = 0; i < n; i++) {
		point p1 = v[i];
		point p2 = v[(i + 1) % n];
		double ang = atan2(p1 ^ p2, p1 * p2);
		// print to_degrees(ang);
		if ((p1 ^ p2) < 0) {
			ang = 2 * M_PI - abs(ang);
		}
		mx = max(mx, ang);
	}
	if (n == 1) {
		printf("0\n");
		return 0;
	} elif (n == 2) {
		point p1 = v[0];
		point p2 = v[1];
		double ang = abs(atan2(p1 ^ p2, p1 * p2));
		printf("%5.15lf\n", min(to_degrees(ang), 360 - to_degrees(ang)));
		return 0;
	}
	printf("%5.15lf\n", 360 - to_degrees(mx));

}//asd