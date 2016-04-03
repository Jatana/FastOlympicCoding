vector<int> prefix_func(const string &s) {
	int n = len(s);
	vector<int> rez(n);
	rez[0] = 0;
	for (int i = 1; i < n; i++) {
		int j = rez[i - 1];
		while (j > 0 && s[j] != s[i]) {
			j = rez[j - 1];
		}
		if (s[j] == s[i]) {
			rez[i] = j + 1;
		} else {
			rez[i] = 0;
		}
	}
	return rez;
}