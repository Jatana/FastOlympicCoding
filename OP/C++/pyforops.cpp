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
#include <array>


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
#define fall(x, seq) for (auto &x : seq) 
#define u2a(seq, function) for (auto &x : seq) { x = function(x); }
#define ifhas(tf, x, map) \
auto x = map.find(tf); \
if (x != map.end()) 
#define ifnhas(tf, map) if (map.find(tf) == map.end()) 
#define fe for_each

using namespace std;

// I/O Stream Manager
namespace IO_Stream {
	template <class T> ostream& operator<< (ostream &os, vector<T> &v) {
		f(i, v.size() - 1) {
			os << v[i] << " ";
		}
		if (!v.empty()) {
			os << v[v.size() - 1];
		}
		return os;
	}

	template <class T> ostream& operator<< (ostream &os, vector<vector<T>> &v) {
		f(i, v.size() - 1) {
			os << v[i];
			os << nl;
		}
		if (!v.empty()) {
			os << v[v.size() - 1];
		}
		return os;
	}

	template <class T_First, class T_Second> ostream& operator<< (ostream &os, pair<T_First, T_Second> &p) {
		os << p.first << " " << p.second;
		return os;
	}

	template <class T> istream& operator>> (istream &is, vector<T> &v) {
		f(i, v.size()) {
			is >> v[i];
		}
		return is;
	}
}

void set_accuracy(int accure) {
	cout << setprecision(accure) << fixed;
}

namespace code_engine {
	template<typename... Ts>
	constexpr auto make_array(Ts&&... ts)
		-> std::array<std::common_type_t<Ts...>, sizeof...(ts)>
	{
		return { std::forward<Ts>(ts)... };
	}
}

namespace defython {
	class xrange;
	class generator;
	using code_engine::make_array;

	class generator {
		
	};
	vector<xrange> xranges;
	class xrange : public generator {
	private:
		static int xranges_stp;
	public:
		bool is_start;
		int n, k, i;
		class range_iterator {
		public:
			bool is_del_callback;
			int *iter;
			operator int() {
				return *iter;
			}

			range_iterator(bool is_del_callback=false) {
				this->is_del_callback = is_del_callback;
				iter = new int;
			}

			range_iterator(int i) {
				iter = new int(i);
			}
			
			void set_value(int value) {
				*iter = value;
			}

			~range_iterator() {
				if (is_del_callback) {
					// cout << endl << "delcalback" << endl;
					delete xranges[xranges.size() - 1].iterator.iter;
					xranges.pop_back();
				} else {
					// delete iter;	
				}
			}

			// range_iterator &operator = (xrange &r) {
			// 	r.iterator = this;
			// 	*(r.iterator->iter) = r.i;
			// 	return *this;
			// }
		};
		
		static range_iterator make_range_iterator() {
			return range_iterator();
		}

		range_iterator iterator;
		// void tie_iterator(int iterator) {
		// 	this->iterator = &iterator;
		// 	*(this->iterator) = this->i;
		// }

		template<class T>
		xrange(T args) {
			// cout << " ----\n";
			// cout << args.size();
			// int i = 0;
			// while(i < args.size()) {
			// 	assert(typeid(args[i]) == typeid(int));
			// 	i++;
			// }
			
			switch (args.size()) {
				case 1:
					this->n = args[0];
					this->k = 1;
					this->i = 0;
					break;
				case 2:
					this->n = args[1];
					this->i = args[0];
					this->k = 1;
					break;
				case 3:
					this->k = args[2];
					this->n = args[1];
					this->i = args[0];
					break;
				default:
					assert(false);
					break;
			}
			is_start = false;
			xranges.push_back(*this);
			// cout << endl << xranges.size() << " -itsreal" << endl;
		}

		xrange() {

		}

		~xrange() {
			// cout << "Hello";
			// xranges.pop_back();
		}

		friend range_iterator operator >> (range_iterator i, xrange r) {
			(xranges[xranges.size() - 1]).iterator = i;
			*((xranges[xranges.size() - 1]).iterator.iter) = ((xranges[xranges.size() - 1]).i);
			return i;
		}

		// bool iteration() {
		// 	if (*(this->iterator) + this->k < this->n) {
		// 		*(this->iterator) += this->k;
		// 		return true;
		// 	}
		// 	return false;
		// }
		
		static bool check_range() {
			if (xranges.empty()) {
				assert(false);
			}
			xrange *cur_gen = &(xranges[xranges.size() - 1]);
			return (*(cur_gen->iterator.iter)) < cur_gen->n;
		}

		static void iterate() {
			if (xranges.empty()) {
				assert(false);
			}
			xrange *cur_gen = &(xranges[xranges.size() - 1]);
			(*(cur_gen->iterator.iter)) += cur_gen->k;
		}


	};
	template<class T>
	xrange make_range(T args) {
		return new xrange(args);
	}

	int xrange::xranges_stp = 0;
	// vector<xrange> xrange::xranges = vector<xrange>();
	template<class T> 
	long long sum(vector<T> &v) {
		long long rez = 0;
		fall(x, v) {
			rez += x;
		}
		return rez;
	}

	template<class T>
	T max(vector<T> &v) {
		if (v.size() == 0) {
			return NULL;
		}
		T assume_max = v[0];
		fall(x, v) {
			if (assume_max < x) {
				assume_max = x;
			}
		}
		return assume_max;
	}	
}

namespace typedefs {
	typedef long long ll;
	typedef unsigned long long ull;
	typedef vector<int> vi;
	typedef pair<int, int> pii;
	typedef vector<vector<pair<int, int>>> vvpii;
	typedef vector<vector<pair<bool, int>>> vvpbi;
}

using namespace IO_Stream;
using namespace typedefs;
using namespace code_engine;
using defython::xrange;

#define range(args...) xrange(make_array(args)), \
ssssssuppperrrrcalllbaccckkkk(true); \
xrange::check_range(); xrange::iterate())
#define for for (xrange::range_iterator 
#define in = xrange::make_range_iterator() >> 

int main(int argc, char *argv[]) {
	
	rt;
}