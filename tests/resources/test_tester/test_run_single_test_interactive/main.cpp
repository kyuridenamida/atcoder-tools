#include <bits/stdc++.h>

#define REP(i,n) for (int i=0;i<(n);++i)

#define N_MAX 26

using namespace std;

typedef pair<int, int> pii;

int N, Q;
string balls;
vector<pii> relations; // (x, y) in relations <=> x < y

void insertBall(int first, int last, char ball)
{
	int mid = first + (last - first) / 2;
	printf("? %c %c\n", balls[mid], ball);
// invalid query
//	printf("? %d %d\n", balls[mid], ball);
	fflush(stdout);
	string ans;
	cin >> ans;
	if (ans == ">") {
		if (last - first == 1) {
			balls.insert(first, 1, ball);
		} else {
			insertBall(first, mid, ball);
		}
	} else if (ans == "<") {
		if (last - first <= 2) {
			balls.insert(last, 1, ball);
		} else {
			insertBall(mid + 1, last, ball);
		}
	}
}

void quit(const string &s){
	cout<<"! ";
	cout<<s;
// wrong answer
//	cout<<"I have a pen!!"<<endl;
	cout<<endl;
	// TLE after judge
//	while(1){}
	exit(0);
}

void solve_N26()
{
	balls = "A";
	for (char ball = 'B'; ball <= 'Z'; ++ball) {
		insertBall(0, balls.size(), ball);
	}
	quit(balls);
}

bool satisfies_relations(int a[])
{
	for (pii rel: relations) {
		if (a[rel.first] >= a[rel.second]) {
			return false;
		}
	}
	return true;
}

void solve_N5()
{
	while (true) {
		// find (query_i, query_j) s.t. d = 2 * q * abs(Probability(ball[query_i] < ball[query_j] | relations) - 1/2) is minimized
		// where q = # { a | a: a permutation of {0,1,...,N-1} that satisfies relations }
		int query_i;
		int query_j;
		int d_min = INT_MAX;
		int q = 0;
		int p[N_MAX][N_MAX]; // p[i][j] = # { a | a: a permutation of {0,1,...,N-1} that satisfies relations and a[i] < a[j] }
	// Probability(ball[i] < ball[j] | relations) = p[i][j] / q
	REP(i, N) REP(j, N) p[i][j] = 0;
	int a[N_MAX];
	REP(k, N) a[k] = k;
	do {
		if (satisfies_relations(a)) {
			++q;
			REP(i, N) REP(j, N) {
				if (a[i] < a[j])
					++p[i][j];
			}
		}
	} while (next_permutation(a, a + N));
	if (q == 1) {
		break;
	}
	REP(i, N) REP(j, N) {
		int d = abs(2 * p[i][j] - q);
		if (d_min > d) {
			d_min = d;
			query_i = i;
			query_j = j;
		}
	}
	printf("? %c %c\n", 'A' + query_i, 'A' + query_j);
	fflush(stdout);
	string ans;
	cin >> ans;
	if (ans == "<") {
		relations.push_back(pii(query_i, query_j));
	} else if (ans == ">") {
		relations.push_back(pii(query_j, query_i));
	}
	}
	int a[N_MAX];
	REP(i, N) a[i] = i;
	do {
		if (satisfies_relations(a)) {
			vector<pii> v;
			REP(i, N) v.push_back(pii(a[i], i));
			sort(v.begin(), v.end());
			string balls = "";
			REP(i, N) balls += 'A' + v[i].second;
			quit(balls);
			break;
		}
	} while (next_permutation(a, a + N));
}

int main(void)
{
//TLE before judge
//	while(1);
	cin >> N >> Q;
	if (N == 26) {
		solve_N26();
	} else if (N == 5) {
		solve_N5();
	}
	return 0;
}

