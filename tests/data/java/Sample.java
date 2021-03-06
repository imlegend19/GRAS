package ext.some.pkg;

import java.lang.Object;
import java.lang.Cloneable;
import org.gras.Person;

/* Subclass Student */
class Student extends Person
{
    void message()
    {
        System.out.println("This is student class");
    }

    // Note that display() is only in Student class
    void display()
    {
        // will invoke or call current class message() method
        message();

        // will invoke or call parent class message() method
        super.message();
    }
}

class Test {
    public static void main(String args[])
    {
        Student s = new Student();
        s.display();
    }
}

interface ConvertibleTo<T> {
    T convert();
}

// Mutually Recursive Type Variable Bounds
class ReprChange<T extends ConvertibleTo<S>, S extends ConvertibleTo<T>> extends ConvertibleTo {
    T t;

    void set(S s) {
        t = s.convert();
    }

    S get() {
        return t.convert();
    }
}

class Seq<T> {
    T head;
    Seq<T> tail;

    Seq() {
        this(null, null);
    }

    Seq(T head, Seq<T> tail) {
        this.head = head;
        this.tail = tail;
    }

    boolean isEmpty() {
        return tail == null;
    }

    class Zipper<S> {
        Seq<Pair<T, S>> zip(Seq<S> that) {
            if (isEmpty() || that.isEmpty()) {
                return new Seq<Pair<T, S>>();
            } else {
                Seq<T>.Zipper<S> tailZipper = tail.new Zipper<S>();
                return new Seq<Pair<T, S>>(new Pair<T, S>(head, that.head), tailZipper.zip(that.tail));
            }
        }
    }
}

class Pair<T, S> {
    T fst;
    S snd;

    Pair(T f, S s) {
        fst = f;
        snd = s;
    }
}

interface I<T> {}

protected class Point {
    int x, y;
    Point(int x, int y) { this.x = x; this.y = y; }
}

public abstract class Sample extends Point implements I<String>, Cloneable {
    class Inner extends Object {
        static final int x = 3; // OK: constant variable
    }

    static class NestedButNotInner {
        static int z = 5; // OK: not an inner class
    }

    interface NeverInner {
    } // Interfaces are never inner

    public static void main(String[] args) {
        Seq<String> strs = new Seq<String>("a", new Seq<String>("b", new Seq<String>()));
        Seq<Number> nums = new Seq<Number>(new Integer(1), new Seq<Number>(new Double(1.5), new Seq<Number>()));

        Seq<String>.Zipper<Number> zipper = strs.new Zipper<Number>();

        Seq<Pair<String, Number>> combined = zipper.zip(nums);

        System.out.println(combined);
    }
}
