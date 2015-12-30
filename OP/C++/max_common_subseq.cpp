template<class T>
vector<T> max_common_subseq(vector<T> v1, vector<T> v2) {
	if (v1.size() == 0 || v2.size() == 0) {
		return vector<T>();
	}
	vector<vector<int>> dp(v1.size(), vector<int>(v2.size(), 0));
	vector<vector<int>> prev(v1.size(), vector<int>(v2.size(), -1));
	prev[0][0] = -2;
	if (v1[0] == v2[0]) {
		dp[0][0] = 1;
		prev[0][0] = 0;
	}
	
	for (int i = 1; i < v1.size(); i++) {
		if (v1[i] == v2[0]) {
			dp[i][0] = 1;
			prev[i][0] = 0;
		} else {
			dp[i][0] = dp[i - 1][0];
			prev[i][0] = -1;
		}
	}
	for (int i = 1; i < v2.size(); i++) {
		if (v2[i] == v1[0]) {
			dp[0][i] = 1;
			prev[0][i] = 0;
		} else {
			dp[0][i] = dp[0][i - 1];
			prev[0][i] = 1;
		}
	}
	for (int i = 1; i < v1.size(); i++) {
		for (int j = 1; j < v2.size(); j++) {
			if (v1[i] == v2[j]) {
				dp[i][j] = dp[i - 1][j - 1] + 1;
				prev[i][j] = 0;
			} else if (dp[i - 1][j] > dp[i][j - 1]) {
				dp[i][j] = dp[i - 1][j];
				prev[i][j] = -1;
			} else {
				dp[i][j] = dp[i][j - 1];
				prev[i][j] = 1;
			}
		}
	}
	int y = v1.size() - 1, x = v2.size() - 1;
	vector<T> rez;
	while (y >= 0 && x >= 0) {
		if (prev[y][x] == 0) {
			rez.push_back(v1[y]);
			y--;
			x--;
		} else if (prev[y][x] == -1) {
			y--;
		} else {
			x--;
		}
	}
	reverse(rez.begin(), rez.end());
	return rez;
}