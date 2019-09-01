using System;
using System.Text;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using static System.Console;
using static System.Math;
using System.Diagnostics;

public class Program{
    {% if mod %}
    const long MOD = {{ mod }};
    {% endif %}
    {% if yes_str %}
    const string YES = "{{ yes_str }}";
    {% endif %}
    {% if no_str %}
    const string NO = "{{ no_str }}";
    {% endif %}

    public static void Main(string[] args){
        ConsoleInput cin = new ConsoleInput(Console.In, ' ');
        {% if prediction_success %}
        {{ input_part }}
        new Program().Solve({{ actual_arguments }});
        {% else %}
        // Failed to predict input format
        {% endif %}
    }

    {% if prediction_success %}
    public void Solve({{ formal_arguments }}){
        
    }
    {% endif %}
}

public class ConsoleInput{
    private readonly System.IO.TextReader _stream;
    private char _separator = ' ';
    private Queue<string> inputStream;
    public ConsoleInput(System.IO.TextReader stream, char separator = ' '){
        this._separator = separator;
        this._stream = stream;
        inputStream = new Queue<string>();
    }
    public string Read{
        get{
            if (inputStream.Count != 0) return inputStream.Dequeue();
            string[] tmp = _stream.ReadLine().Split(_separator);
            for (int i = 0; i < tmp.Length; ++i)
                inputStream.Enqueue(tmp[i]);
            return inputStream.Dequeue();
        }
    }
    public string ReadLine { get { return _stream.ReadLine(); } }
    public int ReadInt { get { return int.Parse(Read); } }
    public long ReadLong { get { return long.Parse(Read); } }
    public double ReadDouble { get { return double.Parse(Read); } }
    public string[] ReadStrArray(long N) { var ret = new string[N]; for (long i = 0; i < N; ++i) ret[i] = Read; return ret;}
    public int[] ReadIntArray(long N) { var ret = new int[N]; for (long i = 0; i < N; ++i) ret[i] = ReadInt; return ret;}
    public long[] ReadLongArray(long N) { var ret = new long[N]; for (long i = 0; i < N; ++i) ret[i] = ReadLong; return ret;}
}
