/*
																									 
											 `-:://:::-                                             
										   `//:-------:/:`                                          
										  .+:--.......--:+`                                         
										 `+:--..`````..--//`                                        
										 .o:--..`` ``..--:o`                                        
										 .o:--...```..---+/`                                        
									   `/y+o/---....---:+o.                                         
								   `...````-os+/:---:/+o/--.`                                       
			  `-/+++++/:.      `...`       :h+d+oooo+/+-`   ...                                     
			`/++//:::://++-`....`         -.`//````````:`     `..`                                  
		   `o+/::------://o/`           `-` -.          -`       `..`                               
 `---.-o/:./o/::-..``..-ЗАПУСКАЕМ      ..  ..            -`        `...       ``..``                
  `....o+:-++/:--.```..-://s.        `-`  .-              -`          `-o: .-//::::/:-`             
		  `:s+/:--....-::/+s-`      .-   `-                -`           -///:--------:/:`           
		   ./s+//:::::://oo-``..НЕЙРОННУЮ: СЕТЬ:::::::-`РАБОТЯГИ        `+:--........--:/`          
			.:ooo+++++osso-`    `.:-...`/` ./::-------:/:`   -`         :+--..``````.--:+:...-+:-`  
			 `.-/+++++/+-.-`    -.   ``:so:/:--.......--:+`  `-```````o+/+--..`````..--:o/-..:s+:.  
				 ```````:``.. `-`     -` `+:--..`````..--/+-.../.`````..-o:--.......---/o.    `     
						`:  `:-      -.  .o:--..`` ``..--:o`   `-`      `:o+:--------:+o-`          
						 `-`-...    ..   .o/--...```..--:+/`    `-`     `oy/so/////++o/.`           
						  -/`  `-` `- ``+s/o/:---...---:++.      `-`   .-../d://///:-.`             
				`.---..``-..-    .-/..`````-oo+/:::::/+o+-        `-``-`  `-.  ````                 
			 `:++++/+++++-  ..``.-/:`      /y-:/++o++/:.`..`       ./.   `-                         
			-++/::::::://+/..:-``:` ..   `-.`  ```.```    `..`   `..`-` `-                          
	   ``  -o//:--....-::/++` -.-`   `-`.-`                 `..`..`  `-.-                           
  -----ss+:++/:--.```..-://s.  /.     `::                    `-:.     ./`                           
  `````/:..+o/::-..``.--:/+s. ..-`   `-``-`                 ..` `-`  `-`-`                          
		  `-s+/::-----::/+oo---``-` ..    .:-    ```      .-`     .-.-  `-`                         
		   `:oo+//::://+os/..:`..-/:`      :y.-:::::::.`.-`        ./-`  `-`                        
			`./+oooooooo+/.`-    .-:...`.. .//:-------://`        `- `..` `:.                       
			  ``.-::::-.``-/`  `-` `-  `oo:+:--.......--:/`      `-    `.:--h.``..```               
						  -.-`.-    .-   `+:--..`````..--//`    `-       /s-//::::::::.             
						 -` `/-      ..  .o:--..`` ``..--:o.```.-        `//:--------://`           
						-` .-`.-`     -.`-o/--...```..--:+/.``-:....``:-.+:--....`...--:+`          
					   ..`-.   `-.   ``:os:o/:---...---:++.  `-     ``///+:-..``````.--:+-````-.`   
			  `.:///////.-`      .:-..` -``-+o+/:::::/+o/.  `-         `:+:-..`````..--:o/:--/ys+-  
			`-++///////+o/. ``....`-.    :` `.:++++++/:.`  .-           -o/---......---/o.   `.`    
		   `++//:-----::/+o:..`     .-`   :    ```````    .-           `+so+:--------:++-`          
  `````:-``:o/::-..`..--:/+o`         -.  `-             .-          `../../+o+////+o+:.`           
  -----syo/o+/:--.```..-://s.          .-` `-           .-        `...     ``-:////:-``             
	   .` `/s//:--....-::/+s.            -. `-`        .-       `..`                                
		   .+o+/:::--:://+s/-..`          .::+y  ```  .-     `..`                                   
			./oo++////+oso-`   `....       :y-+:::::::/`   ...                                      
			 `.:+oooooo/-`         `....-. .//:-------:/:-.`                                        
				``...``                 /+:+:--.......--:+`                                         
										 `+:--..`````..--//`                                        
										 .o:--..`` ``..--:o`                                        
										 .+/--...```..--:+/`                                        
										 `-o/:---...---:++.                                         
										  `-+o+/:---:/+o/.                                          
											`.:+oooo+/-.`                                           
											   ``````                                               
*/


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
#include <bitset>
#include <functional>
#include <ext/pb_ds/tree_policy.hpp>
#include <ext/pb_ds/assoc_container.hpp>


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
}

namespace numbers_operation {
	template<class T>
	T floor_mod(T a, T b) {
		if (a % b == 0) return 0;
		if (a >= 0 && b >= 0) return a % b;
		if (a <= 0 && b <= 0) return a % b;
		return abs(b) - (abs(a) % abs(b));
	}
}

using namespace numbers_operation;
using namespace typedefs;
using namespace __gnu_pbds;


#define print    \
smart_io::precall_print(); \
cout,

#define scan cin,
#define int long long



struct Point {
	int x, y;
	int id;

	Point(int _x, int _y, int _id=-1) {
		x = _x;
		y = _y;
		id = _id;
	}

	Point operator-(const Point &p) {
		return Point(x - p.x, y - p.y);
	}

	int operator^(const Point &other) {
		return x * other.y - y * other.x;
	}

	tuple<int, int, int> to_tuple() const {
		return make_tuple(x, y, id);
	}

	bool operator<(const Point &other) const {
		return to_tuple() < other.to_tuple();
	}
};

struct point_less {
	bool operator()(const Point &a, const Point &b) {
		return a < b;
	}
};

typedef tree<Point, null_type, less<Point>, rb_tree_tag, tree_order_statistics_node_update> ordset;
int n;
vector<Point> base_points;


vector<Point> convex_hully() {
	Point dp = base_points[0];
	for (Point p : base_points) {
		if (mp(p.y, p.x) < mp(dp.y, dp.x)) {
			dp = p;
		}
	}

	vector<Point> v;
	for (Point p : base_points) {
		if (p.id != dp.id) {
			v.pb(p);
		}
	}

	sort(v.begin(), v.end(), [dp](Point a, Point b) {
		return atan2(a.y - dp.y, a.x - dp.x) < atan2(b.y - dp.y, b.x - dp.x);
	});

	vector<Point> rez {dp, v[0]};

	for (int i = 1; i < len(v); i++) {
		Point base = rez.back();
		Point next = v[i] - base;
		Point prev = rez[len(rez) - 2] - base;
		while (len(rez) >= 2 && ((next ^ prev) < 0)) {
			rez.pop_back();
			if (len(rez) < 2) break;
			base = rez.back();
			next = v[i] - base;
			prev = rez[len(rez) - 2] - base;
		}
		rez.pb(v[i]);
	}
	return rez;
}


bool in(const vector<Point> &poly) {
	cout << "? " << len(poly);
	for (Point p : poly) {
		cout << ' ' << (p.id + 1);
	}
	cout << endl;
	string resp;
	cin >> resp;
	return resp == "Yes";
}

int square_x2(vector<Point> tri) {
	return abs((tri[1] - tri[0]) ^ (tri[2] - tri[0]));
}

bool in_tri(const vector<Point> &tri, Point p) {
	return square_x2({tri[0], tri[1], p})
		+ square_x2({tri[1], tri[2], p})
		+ square_x2({tri[0], tri[2], p}) == square_x2(tri);
}

vector<Point> random_shift(const vector<Point> &points) {
	int shift = abs(rand());
	vector<Point> rez = points;

	for (int i = 0; i < len(points); i++) {
		rez[(i + shift) % len(points)] = points[i];
	}
	return rez;
}

signed main(signed argc, char *argv[]) {
	srand(1337);
	cin >> n;
	for (int i = 0; i < n; i++) {
		int x, y;
		cin >> x >> y;
		base_points.pb(Point(x, y, i));
	}
	// print in_tri({base_points[0], base_points[4], base_points[5]}, base_points[3]);

	vector<Point> convex = convex_hully();

	int cnt_q;
	cin >> cnt_q;
	for (int q = 0; q < cnt_q; q++) {
		vector<Point> tri;
		int left = 1;
		int right = len(convex) - 1;
		while (right - left > 1) {
			int mid = (left + right) / 2;
			vector<Point> query;
			for (int i = 0; i <= mid; i++) {
				query.pb(convex[i]);
			}
			if (in(query)) {
				right = mid;
			} else {
				left = mid;
			}
		}
		tri = {convex[0], convex[right], convex[right - 1]};

		vector<Point> ava = base_points;
		random_shuffle(ava.begin(), ava.end());
		vector<Point> to_del;
		while (!ava.empty()) {
			Point sub = ava.back();
			if (sub.id == tri[0].id
				|| sub.id == tri[1].id
				|| sub.id == tri[2].id
				|| !in_tri(tri, sub)) {
				ava.pop_back();
				continue;
			}
			
			if (in({tri[0], tri[1], sub})) {
				tri = {tri[0], tri[1], sub};
			} else if (in({tri[1], tri[2], sub})) {
				tri = {tri[1], tri[2], sub};
			} else {
				tri = {tri[0], tri[2], sub};
			}
		}
		cout << "! 3 " << (tri[0].id + 1) << " " << (tri[1].id + 1) << " " << (tri[2].id + 1) << endl;
	}
}