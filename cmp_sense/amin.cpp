vector<int> dijkstra(vector<vector<pair<int, int>>> &vertices, int n, int v, int to_v) {
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
	q.push(make_pair(v, 0));
	dist[v] = 0;
	while (!q.empty()) {
		int cur_v, weight;
		tie(cur_v, weight) = q.top();

		q.pop();
		if (visited[cur_v] && dist[cur_v] < weight) {
			continue;
		}
		visited[cur_v] = true;
		dist[cur_v] = weight;
		for (auto p : vertices[cur_v]) {
			if (!visited[p.first]) {
				q.push(make_pair(p.first, p.second + dist[cur_v]));
				dist[p.first] = p.second + weight;
				prev[p.first] = cur_v;
				visited[p.first] = true;
			} else {
				if (dist[p.first] > dist[cur_v] + p.second) {
					q.push(make_pair(p.first, p.second + dist[cur_v]));
					dist[p.first] = dist[cur_v] + p.second;
					prev[p.first] = cur_v;
				}
			}
		}
	}
	int ind = to_v;
	vector<int> way;
	while (prev[ind] != -1) {
		way.push_back(ind);
		ind = prev[ind];
	}
	way.push_back(v);
	reverse(way.begin(), way.end());
	//return way;
	return dist;
}