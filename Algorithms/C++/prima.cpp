vector<int> prima(vector<vector<pair<int, int>>> &vertices, int n, int v) {
	if (n < 1) {
		return vector<int>();
	}
	vector<bool> visited(n, false);
	vector<int> dist(n, -1);
	vector<int> prev(n, -1);
	auto cmp = [](pair<int, int> &a, pair<int, int> &b){
		return a.second > b.second;
	};
	priority_queue<pair<int, int>, vector<pair<int, int>>, decltype(cmp)> q(cmp);
	dist[v] = 0;
	q.push(make_pair(v, 0));
	while (!q.empty()) {
		int cur_v, weight;
		tie(cur_v, weight) = q.top();
		q.pop();
		if (visited[cur_v]) {
			continue;
		}
		visited[cur_v] = true;
		dist[cur_v] = weight;
		for (auto p : vertices[cur_v]) {
			if (!visited[p.first]) {
				q.push(make_pair(p.first, p.second));
				prev[p.first] = cur_v;
			}
		}
	}
	for (auto x : visited) {
		assert(x);
	}
	return dist;
}