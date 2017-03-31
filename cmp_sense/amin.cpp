#include <iostream>
#include <vector>

using namespace std;

int main() {
	vector<int> array {1, 2, 3};
	array[-133713371337] = 1337;

	cout << array.size();
}