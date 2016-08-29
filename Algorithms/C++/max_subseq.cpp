vector<int> max_subseq(vector<int> v) {
	int n = v.size();
	if (n <= 0) {
		return vector<int>();
	} 
	vector<pair<int, int>> dp(1);
	vector<int> prev(n);

	for (int i = 0; i < n; i++) {
		int left = 0;
		int right = dp.size();
		while (right - left > 1) {
			int mid = (right + left) / 2;
			if (dp[mid].first < v[i])  {
				left = mid;
			} else {
				right = mid;
			}
		}
		if (left != 0) {
			prev[i] = dp[left].second;
		} else {
			prev[i] = -1;
		}
		if (left + 1 < dp.size()) {
			if (dp[left + 1].first > v[i]) {
				dp[left + 1].first = v[i];
				dp[left + 1].second = i;
			}
		} else {
			dp.push_back(make_pair(v[i], i));
		}
	}
	vector<int> rez;
	int x = dp[dp.size() - 1].second;
	while (x != -1) {
		rez.push_back(v[x]);
		x = prev[x];
	}
	reverse(rez.begin(), rez.end());
	return rez;
}