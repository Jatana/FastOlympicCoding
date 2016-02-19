template <class T>
class tree_segment {
public:
	vector<T> tree;
	function<T (T, T)> magic;
	T null_object;
	int delta;
	int added_delta;
	int n;
private:
	int get_next_pow2(int n) {
		int k = log2(n);
		if (pow(2, k) < n) {
			return pow(2, k + 1);
		}
		return pow(2, k);
	}

	void __update(int ind, T k) {
		tree[ind] = magic(tree[ind], k);
		if (ind != 0) {
			int sub = (ind - 1) / 2;
			__update(sub, k);
		}
	}

	T __query(int v, int q_left, int q_right, int ths_left, int ths_right) {
		// cout << v << " -verte\n";
		// if (v == 4) {
		// 	cout << ths_left << " " << ths_right << nl;
		// 	cout << q_left << " " << q_right << nl;
		// }
		if (q_right <= ths_left || q_left >= ths_right) {
			return null_object;
		}
		if (q_left <= ths_left && ths_right <= q_right) {
			return tree[v];
		}
		int center = (ths_left + ths_right) / 2;
		return magic(__query((v * 2) + 1, q_left, q_right, ths_left, center)
					 ,__query((v * 2) + 2, q_left, q_right, center, ths_right));
	}

public:

	void makify() {
		// TODO
		int n = tree.size();
		for (int i = n - 1; i > -1; i--) {
			int sub1 = (i * 2) + 1;
			int sub2 = (i * 2) + 2;
			if (sub1 < n && sub2 < n) {
				tree[i] = magic(tree[sub1], tree[sub2]);
			}
		}
	}
	
	tree_segment(vector<T> v, function<T (T, T)> magic, T null_object)
			:magic(magic), null_object(null_object) {
		int n = v.size();
		int n_pref = (get_next_pow2(n) * 2) - 1;
		tree.resize(n_pref);
		this->delta = n_pref - n;
		this->n = get_next_pow2(n);
		this->added_delta = this->n - v.size();
		for (int i = 0; i < n; i++) {
			int j = n_pref - v.size() + i;
			tree[j] = v[i];
		}
		makify();
	}

	void update(int ind, T k) {
		__update(delta + ind, k);
	}

	T query(int left, int right) {
		return __query(0, added_delta + left, added_delta + right, 0, n);
	}

};