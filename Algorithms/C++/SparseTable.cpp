template <class T, class T_Magic>
class SparseTable {
public:
	T_Magic magic;
	vector<int> two_powers{1};
	vector<int> max_pow2;
	vector<vector<T>> tree;
private:
	int next_2log(int n) {
		int x = log2(n);
		if (n != pow(x, 2)) {
			x++;
		}
		return x;
	}

	T __query(int left, int right) {
		int block = max_pow2[right - left + 1];
		return magic(tree[block][left], tree[block][right - (two_powers[block]) + 1]);
	}
public:
	SparseTable(vector<T> &v, T_Magic magic):magic(magic) {
		int n = v.size();
		int logn = log2(n) + 1;

		if (two_powers.empty()) {
			two_powers.pb(1);
		}
		while (two_powers.size() <= logn) {
			two_powers.pb(2 * two_powers[two_powers.size() - 1]);
		}

		// max_pow2 construction
		max_pow2.resize(n + 1, 1);
		int cur_pow = 1;
		int cur_log = 0;
		for (int i = 0; i < n + 1; i++) {
			if (i >= cur_pow) {
				cur_pow *= 2;
				cur_log++;
			}
			max_pow2[i] = max(cur_log - 1, 0);
		}
		// cout << max_pow2 << nl;
		// exit(0);
		tree.resize(logn, vector<T> (n));
		tree[0] = v;
		construct_tree();
	};

	void construct_tree() {
		for (int i = 1; i < tree.size(); i++) {
			for (int j = 0; j < tree[i].size(); j++) {
				int next_block = j + two_powers[i - 1];
				tree[i][j] = tree[i - 1][j];
				if (next_block < tree[i - 1].size()) {
					tree[i][j] = magic(tree[i][j], tree[i - 1][next_block]);
				}
			}
		}
	}
	
	// calcs magic in [L:R)
	T query(int left, int right) {
		right--;
		if (left > right) {
			tie(left, right) = mt(right, left);
		}
		return __query(left, right);
	}

};
