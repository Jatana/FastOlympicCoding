vvi floyd(vector<vector<pair<bool, int>>> &matrix) {
	int n = matrix.size();
	vvi next(n, vector<int>(n, -1));
	f (i, n) {
		f (j, n) {
			if (matrix[i][j].first) {
				next[i][j] = j;
			}
		}
	}
	f (k, n) {
		f (i, n) {
			f (j, n) {
				if (matrix[i][k].first && matrix[k][j].first) {
					if (!matrix[i][j].first || (matrix[i][j].second > matrix[i][k].second + matrix[k][j].second)) {
						matrix[i][j].first = true;
						matrix[i][j].second = matrix[i][k].second + matrix[k][j].second;
						next[i][j] = next[i][k];
					}
				}
			}
		}
	}
	return next;
}