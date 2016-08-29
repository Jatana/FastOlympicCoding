template<class T>
class heap {
public:
	vector<T> v;
	function<bool (T &a, T &b)> cmp = [](T &a, T &b){return a < b;};

	heap() {

	}

	heap(bool cmp(T &a, T &b)): cmp(cmp) {
	}

	heap(vector<T> v, bool cmp(T &a, T &b)): cmp(cmp), v(v) {
	}

	void up(int ind) {
		int sub = (ind - 1) >> 1;
		while (ind != 0 && cmp(v[ind], v[sub])) {
			tie(v[ind], v[sub]) = mt(v[sub], v[ind]);
			ind = sub;
			sub = (ind - 1) >> 1;
		}
	}

	void down(int ind) {
		int sub = (ind << 1) + 1;
		sub = (sub + 1 >= v.size() || cmp(v[sub], v[sub + 1])) ? sub : sub + 1;
		while (sub < v.size() && cmp(v[sub], v[ind])) {
			tie(v[ind], v[sub]) = mt(v[sub], v[ind]);
			ind = sub;
			sub = (ind << 1) + 1;
			sub = (sub + 1 >= v.size() || cmp(v[sub], v[sub + 1])) ? sub : sub + 1;
		}
	}

	void add(T x) {
		v.pb(x);
		up(v.size() - 1);
	}

	T pop() {
		T x = v[0];
		tie(v[0], v[v.size() - 1]) = mt(v[v.size() - 1], v[0]);
		v.ppb();
		down(0);
		return x;
	}

	T top() {
		return v[0];
	}

	bool empty() {
		return v.empty();
	}

	void clear() {
		v.clear();
	}
};