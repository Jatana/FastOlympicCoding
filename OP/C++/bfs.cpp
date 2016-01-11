#include <queue>

vector<int> bfs(vector<vector<int>> vertices, int n, int v) {
	vector<int> dist(n, -1);
	vector<bool> visited(n, false);
	vector<int> prev(n, -1);
	deque<int> d;
	d.push_back(v);
	dist[v] = 0;
	while (!d.empty()) {
		int cur_v = d[0];
		visited[cur_v] = true;
		d.pop_front();
		for (auto x : vertices[cur_v]) {
			if (!visited[x]) {
				d.push_back(x);
				dist[x] = dist[cur_v] + 1;
				prev[x] = cur_v;
			}
		}
	}
	return dist;
}