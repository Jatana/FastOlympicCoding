template <class T>
class fenvik_tree {
private:
	int left_func(int x) {
		return x & (x + 1);
	}

	int up_func(int x) {
		return x | (x + 1);
	}
	
	T __query(int right) {
		T r = null_object;
		while (right >= 0) {
			r = magic(tree[right], r);
			right = left_func(right) - 1;
		}
		return r;
	}

public:
	T null_object;
	vector<T> tree;
	function<T (T, T)> magic;
	function<T (T, T)> invert_magic;
	
	void update(int ind, T dx) {
		while (ind < tree.size()) {
			tree[ind] = magic(tree[ind], dx);
			ind = up_func(ind);
		}
	}

	T query(int left, int right) {
		T r = __query(right);
		if (left > 0) {
			r = invert_magic(r, __query(left - 1));
		}
		return r;
	}

	fenvik_tree(vector<T> prot, decltype(magic) magic, decltype(invert_magic) invert_magic, T null_object)
		: magic(magic), invert_magic(invert_magic), null_object(null_object) {

		int n = prot.size();
		tree.resize(n, null_object);
		for (int i = 0; i < n; i++) {
			update(i, prot[i]);
		}
	}

};