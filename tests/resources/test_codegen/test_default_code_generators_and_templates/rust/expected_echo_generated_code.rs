use io::*;
use std::*;

const MOD: i64 = 123;
static YES: &'static str = "yes";
static NO: &'static str = "NO";
fn solve(N: i64, M: i64, H: Vec<Vec<String>>, A: Vec<i64>, B: Vec<f64>, Q: i64, X: Vec<i64>) {
    println!("{} {}", N, M);
    assert!(H.len() as i64 == N - 1);
    for i in 0..(N-1) as usize {
        assert!(H[i].len() as i64 == M - 2);
        for j in 0..(M-2) as usize {
            if j > 0 {
                print!(" ")
            }
            print!("{}", H[i][j]);
        }
        print!("\n");
    }

    assert!(A.len() as i64 == N - 1);
    assert!(B.len() as i64 == N - 1);
    for i in 0..(N-1) as usize {
        println!("{} {}", A[i], B[i]);
    }
    println!("{}", Q);
    assert!(X.len() as i64 == M + Q);
    for i in 0..(M+Q) as usize {
        println!("{}", X[i]);
    }
    println!("{}", YES);
    println!("{}", NO);
    println!("{}", MOD);
}

fn main() {
    let con = read_string();
    let mut scanner = Scanner::new(&con);
    let mut N: i64;
    N = scanner.next();
    let mut M: i64;
    M = scanner.next();
    let mut H: Vec<Vec<String>> = vec![vec![String::new(); (M-1-2+1) as usize]; (N-2+1) as usize];
    for i in 0..(N-2+1) as usize {
        for j in 0..(M-1-2+1) as usize {
            H[i][j] = scanner.next();
        }
    }
    let mut A: Vec<i64> = vec![0i64; (N-2+1) as usize];
    let mut B: Vec<f64> = vec![0f64; (N-2+1) as usize];
    for i in 0..(N-2+1) as usize {
        A[i] = scanner.next();
        B[i] = scanner.next();
    }
    let mut Q: i64;
    Q = scanner.next();
    let mut X: Vec<i64> = vec![0i64; (M+Q) as usize];
    for i in 0..(M+Q) as usize {
        X[i] = scanner.next();
    }
    // In order to avoid potential stack overflow, spawn a new thread.
    let stack_size = 104_857_600; // 100 MB
    let thd = std::thread::Builder::new().stack_size(stack_size);
    thd.spawn(move || solve(N, M, H, A, B, Q, X)).unwrap().join().unwrap();
}

pub mod io {
    use std;
    use std::str::FromStr;

    pub struct Scanner<'a> {
        iter: std::str::SplitWhitespace<'a>,
    }

    impl<'a> Scanner<'a> {
        pub fn new(s: &'a str) -> Scanner<'a> {
            Scanner {
                iter: s.split_whitespace(),
            }
        }

        pub fn next<T: FromStr>(&mut self) -> T {
            let s = self.iter.next().unwrap();
            if let Ok(v) = s.parse::<T>() {
                v
            } else {
                panic!("Parse error")
            }
        }

        pub fn next_vec_len<T: FromStr>(&mut self) -> Vec<T> {
            let n: usize = self.next();
            self.next_vec(n)
        }

        pub fn next_vec<T: FromStr>(&mut self, n: usize) -> Vec<T> {
            (0..n).map(|_| self.next()).collect()
        }
    }

    pub fn read_string() -> String {
        use std::io::Read;

        let mut s = String::new();
        std::io::stdin().read_to_string(&mut s).unwrap();
        s
    }

    pub fn read_line() -> String {
        let mut s = String::new();
        std::io::stdin().read_line(&mut s).unwrap();
        s.trim_right().to_owned()
    }
}
