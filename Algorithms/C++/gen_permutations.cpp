template<class T>

void gen_permutations(vector<T> picked, vector<pair<T, int>> &objs, int n) {
	if (picked.size() == n) {
		// do some on pickup generated
		for (int i = 0; i < n; i++) {
			cout << picked[i] << " ";
		}
		cout << endl;
	} else {
		for (auto &x : objs) {
			if (x.second > 0) {
				x.second--;
				picked.push_back(x.first);
				gen_permutations(picked, objs);
				picked.pop_back();
				x.second++;
			}
		}
	}
}