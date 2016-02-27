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

#define nl "\n"
#define x first
#define y second
#define pb push_back
#define ppb pop_back
#define pf push_front
#define ppf pop_front
#define mt make_tuple
#define mp make_pair
#define umap unordered_map
#define uset unordered_set
#define Yes "Yes"
#define No "No"
#define YES "YES"
#define NO "NO"
#define rt return 0
#define elif else if
#define f(i, n) for (int i = 0; i < n; i++)
#define fr(i, n) for (int i = n - 1; i > -1; i--)
#define fk(i, begin, n, k) for (int i = begin; i < n; i += k)
#define fall(x, seq) for (auto& x : seq)
#define u2a(seq, function) \
    for (auto& x : seq) {  \
        x = function(x);   \
    }
#define ifhas(tf, x, map) \
    \
auto x = map.find(tf);    \
    \
if(x != map.end())
#define ifnhas(tf, map) if (map.find(tf) == map.end())
#define fe for_each

using namespace std;

// I/O Stream Manager
namespace Smart_IO_Stream {

template <class T_First, class T_Second>
ostream& operator<<(ostream& os, pair<T_First, T_Second>& p)
{
    os << p.first << " " << p.second;
    return os;
}

template <class T>
ostream& operator<<(ostream& os, vector<T>& v)
{
    f(i, v.size() - 1)
    {
        os << v[i] << " ";
    }
    if (!v.empty()) {
        os << v[v.size() - 1];
    }
    return os;
}

template <class T>
ostream& operator<<(ostream& os, vector<vector<T> >& v)
{
    f(i, v.size() - 1)
    {
        os << v[i];
        os << nl;
    }
    if (!v.empty()) {
        os << v[v.size() - 1];
    }
    return os;
}


template <class T_First, class T_Second>
istream& operator>>(istream& is, pair<T_First, T_Second>& p)
{
    is >> p.first >> p.second;
    return is;
}

template <class T>
istream& operator>>(istream& is, vector<T>& v)
{
    f(i, v.size())
    {
        is >> v[i];
    }
    return is;
}
}// namespace Smart_IO_Stream

void set_accuracy(int accure)
{
    cout << setprecision(accure) << fixed;
}

namespace defython {
// vector<xrange> xrange::xranges = vector<xrange>();
template <class T>
long long sum(vector<T>& v)
{
    long long rez = 0;
    fall(x, v)
    {
        rez += x;
    }
    return rez;
}

template <class T>
T max(vector<T>& v)
{
    if (v.size() == 0) {
        return NULL;
    }
    T assume_max = v[0];
    fall(x, v)
    {
        if (assume_max < x) {
            assume_max = x;
        }
    }
    return assume_max;
}
}// namespace defython

namespace typedefs {
typedef long long ll;
typedef unsigned long long ull;
typedef vector<int> vi;
typedef pair<int, int> pii;
typedef vector<vector<pair<int, int> > > vvpii;
typedef vector<vector<pair<bool, int> > > vvpbi;
}

using namespace Smart_IO_Stream;
using namespace typedefs;
#define int ll
int up_div(int a, int b) {
	if (a % b != 0) {
		return (a / b) + 1;
	}
	return a / b;
}
#undef int
int main(int argc, char *argv[]) {
#define int ll
	{
		bool is_debug = false;
		if (argc > 1 && string(argv[1]) == "-debug") {
			is_debug = true;
		}
		if (!is_debug) {
			freopen("parentheses.in", "r", stdin);
			freopen("parentheses.out", "w", stdout);
		}
	}
	int n, nth;
	cin >> n >> nth;
	n <<= 1;
	int max_n = n + 1;
	int max_k = n + 3;

	/*
		dp place n brackets
		and k opens
		correctly
	*/
	vector<vector<int>> dp(max_n, vector<int>(max_n, 0));
	dp[0][0] = 1;
	for (int i = 0; i < max_n; i++) {
	}
	/*
		fill dp
		// derbmo dp
		if n, k norm :
		  if insert ( :
		  	dp[i - 1][j - 1]
		  if insert ) :
		  	dp[i - 1][j]

		// range important
	*/
	for (int i = 1; i < max_n; i++) {
		for (int j = up_div(i, 2); j <= i; j++) {

			if (j > 0) {
				dp[i][j] += dp[i - 1][j - 1];
			}
			if (j < max_k - 1) {
				dp[i][j] += dp[i - 1][j];
			}
		}
	}
	// cout << dp[3][2] << nl;
	// cout << dp[3][2] << nl;
	/*	
		int sm = 0;
		for (auto x : dp[24]) sm += x;
		cout << sm << " ";
	*/
	nth--;
	int cnt_open = 0, cur_n = n, cnt_close = 0;
	string rez = "";
	while (cur_n > 0) {
		// if (cnt_open - cnt_close == 0) {
		// 	rez.pb('(');
		// 	cnt_open++;
		// 	cur_n--;
		// 	continue;
		// }
		// if (cnt_open == cur_n) {
		// 	rez.pb(')');
		// 	cur_n--;
		// }
		int bal = cnt_open + 1 - cnt_close;
		assert((cur_n + bal - 1) % 2 == 0);
		int x_dop = dp[cur_n - 1][(cur_n + bal - 1) / 2];
		// printf("dp<%d, %d> = %d>\n", cur_n - 1, (cur_n + bal - 1) / 2, x_dop);
		// cout << x_dop << " ";
		if (x_dop > nth) {
			rez.pb('(');
			cnt_open++;
			cur_n--;
			continue;
		} else {
			nth -= x_dop;
			rez.pb(')');
			cnt_close++;
			cur_n--;
			// cout << "closed" << " " ;
			// cout << nth << nl;
			// cnt_open = 0;
			continue;
		}
	}
	cout << rez;
	rt;
}