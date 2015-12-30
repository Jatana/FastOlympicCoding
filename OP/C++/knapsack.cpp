vector<int> knapsack(vector<int> weight, vector<int> cost, int w) {
	w++;
	int n = weight.size();

	vector<vector<int>>dp(n + 1, vector<int>(w, -1));
	vector<vector<int>>prev(n + 1, vector<int>(w, -1));
	for (int i = 0; i < n + 1; i++) {
		dp[i][0] = 0;
	}
	for (int i = 1; i < w; i++) {
		for (int j = 1; j < n + 1; j++) {
			if (weight[j - 1] <= i) {
				if (dp[j - 1][i - weight[j - 1]] != -1) {
					dp[j][i] = dp[j - 1][i - weight[j - 1]] + cost[j - 1];
					prev[j][i] = 1;
				}
				if (dp[j - 1][i] != -1) {
					if (dp[j - 1][i] > dp[j][i]) {
						dp[j][i] = dp[j - 1][i];
						prev[j][i] = 0;
					}
				}
			} else {
				dp[j][i] = dp[j - 1][i];
				prev[j][i] = 0;
			}
		}
	}
	int ind = 0;
	for (int i = w - 1; i > -1; i--) {
		if (dp[n][i] != -1) {
			if (dp[n][i] > dp[n][ind]) {
				ind = i;
			}
		}
	}
	vector<int> rez;

	int j = n;
	while (j != 0) {
		if (prev[j][ind] == 0) {
			j--;
		} else if (prev[j][ind] == 1) {
			rez.push_back(j - 1);
			ind -= weight[j - 1];
			j--;
		} else {
			j--;
		}
	}
	reverse(rez.begin(), rez.end());
	return rez;
}