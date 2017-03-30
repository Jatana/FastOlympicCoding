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

#define print    \
smart_io::precall_print(); \
cout,

#define scan cin,
#define int long long
int n, m;
vector<vector<int>> vertices;
vector<bool> visited;
int edges = 0;

void dfs(int v) {
	visited[v] = true;
	for (int subv : vertices[v]) {
		edges++;
		if (visited[subv]) continue;
		dfs(subv);
	}
}

vector<vector<int>> bridges_at;
int bridges = 0;
vector<int> time_in;
vector<int> min_time;
int timer = 0;
set<pii> b;
void find_bridges(int v, int p) {
	visited[v] = true;
	time_in[v] = timer++;
	min_time[v] = time_in[v];
	for (int subv : vertices[v]) {
		if (subv == p) continue;
		if (!visited[subv]) {
			find_bridges(subv, v);
		}
		min_time[v] = min(min_time[v], min_time[subv]);
	}

	for (int subv : vertices[v]) {
		if (subv == p) continue;
		if (min_time[subv] > time_in[v]) {
			bridges_at[v].pb(subv);	
			bridges_at[subv].pb(v);
			bridges++;
			b.insert({v, subv});
			b.insert({subv, v});
		}
	}
}


signed main(signed argc, char *argv[]) {
	scan n, m;

	vertices.resize(n);
	vector<int> norm_at(n);
	ll one = 0;
	for (int i = 0; i < m; i++) {
		int f, t;
		scan f, t;
		f--;
		t--;
		one += (f == t);
		vertices[f].pb(t);
		if (f != t) {
			vertices[t].pb(f);
		}
	}

	visited.resize(n, false);
	int base = -1;
	for (int i = 0; i < n; i++) {
		if (!visited[i]) {
			edges = 0;
			dfs(i);
			if (edges > 0) {
				if (base != -1) {
					print 0;
					return 0;
				} else {
					base = i;
				}
			}
		}
	}



	visited = vector<bool>(n, false);
	bridges_at.resize(n);
	time_in.resize(n, -1);
	min_time.resize(n, -1);
	find_bridges(base, -1);
	// print bridges;
	for (int i = 0; i < n; i++) {
		for (int j : vertices[i]) {
			if (b.find({i, j}) == b.end()) {
				norm_at[i]++;
			}
		}
	}
	ll cnt = 0;
	ll glob = 0;
	ll local = 0;
	ll t = 0;
	for (int i = 0; i < n; i++) {
		ll cur = 0;
		for (int j : vertices[i]) {
			// print i, j, m - bridges + len(bridges_at[i]) + len(bridges_at[j]) - 2LL;
			// glob += m - bridges;
			// cur += m - bridges + len(bridges_at[j]) - 1;
		}
		local += ((ll)len(vertices[i]) * ((ll)len(vertices[i]) - 1LL) / 2LL);
	}

	print local;

	// cnt += (m - bridges) * (m - bridges);
	// print (t / 2) + ((ll)(m - bridges) * (ll)(m - bridges - 1LL) / 2LL) + local;
}