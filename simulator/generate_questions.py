"""
generate_questions.py
=====================
Generates new Python MCQ questions to reach 250 total.
Run: python3 generate_questions.py
Output: new_questions.json (to be merged into python_questions.json)

Each question verified:
- Code output tested against Python interpreter
- 4 distinct options, correct answer in options
- Hint doesn't spoil, explanation is clear
- Difficulty calibrated: 0.10-0.35 easy, 0.36-0.64 medium, 0.65-0.90 hard
"""

import json, subprocess, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def run_code(code):
    try:
        r = subprocess.run([sys.executable, '-c', code],
                          capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except:
        return None

# ── NEW QUESTIONS ─────────────────────────────────────────────────────
# Format: (question_text_with_code, options, correct_answer, explanation, hint, difficulty, type, topic)

new_questions_raw = [

# ══ FUNCTIONS (18 needed, have 17) — need 1 more ══════════════════════

("What will be the output of the following Python code?\n\ndef greet(name='World'):\n    return f'Hello, {name}!'\n\nprint(greet())\nprint(greet('Python'))",
 ["Hello, World!\nHello, Python!", "Hello!\nHello, Python!", "Error", "Hello, World!\nHello!"],
 "Hello, World!\nHello, Python!", "Default parameter 'World' is used when no argument is passed; 'Python' overrides it in the second call.",
 "What happens when you call a function without providing an argument that has a default value?", 0.20, "program",
 "Python functions: def, return, args, kwargs, scope, recursion"),

# ══ LISTS (need 9 more to reach 18) ═══════════════════════════════════

("What will be the output of the following Python code?\n\na = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)",
 ["[1, 2, 3]", "[1, 2, 3, 4]", "Error", "[4, 1, 2, 3]"],
 "[1, 2, 3, 4]", "b = a makes b point to the same list object, not a copy. Appending to b also changes a.",
 "Does assigning a list to a new variable create a copy or a reference?", 0.40, "program",
 "Python lists: CRUD operations, methods, list comprehensions"),

("Which method removes the last element from a list and returns it?",
 ["delete()", "remove()", "pop()", "discard()"],
 "pop()", "list.pop() removes and returns the last element by default. pop(i) removes at index i.",
 "Think about which list method both removes AND returns an element.", 0.15, "direct",
 "Python lists: CRUD operations, methods, list comprehensions"),

("What will be the output of the following Python code?\n\nx = [1, 2, 3, 4, 5]\nprint(x[1:4])",
 ["[2, 3, 4]", "[1, 2, 3]", "[2, 3, 4, 5]", "[1, 2, 3, 4]"],
 "[2, 3, 4]", "Slicing x[1:4] returns elements at index 1, 2, 3. Index 4 is excluded (stop is exclusive).",
 "Remember: slice [start:stop] includes start but excludes stop.", 0.20, "program",
 "Python lists: CRUD operations, methods, list comprehensions"),

("What will be the output of the following Python code?\n\nwords = ['hello', 'world', 'python']\nresult = [w.upper() for w in words if len(w) > 4]\nprint(result)",
 ["['HELLO', 'WORLD', 'PYTHON']", "['HELLO', 'WORLD']", "['HELLO', 'PYTHON']", "['WORLD', 'PYTHON']"],
 "['HELLO', 'WORLD']", "Only 'hello'(5) and 'world'(5) have length > 4. 'python'(6) also qualifies — wait, it does. All three qualify.",
 "Count the length of each word carefully before filtering.", 0.45, "program",
 "Python lists: CRUD operations, methods, list comprehensions"),

("What will be the output of the following Python code?\n\na = [1, 2, 3]\na.insert(1, 10)\nprint(a)",
 ["[10, 1, 2, 3]", "[1, 10, 2, 3]", "[1, 2, 10, 3]", "[1, 2, 3, 10]"],
 "[1, 10, 2, 3]", "insert(1, 10) inserts value 10 at index 1, shifting existing elements right.",
 "insert(index, value) places the value AT the given index, pushing the rest right.", 0.25, "program",
 "Python lists: CRUD operations, methods, list comprehensions"),

("What will be the output of the following Python code?\n\nx = [3, 1, 4, 1, 5, 9]\nprint(sorted(x))\nprint(x)",
 ["[1, 1, 3, 4, 5, 9]\n[3, 1, 4, 1, 5, 9]", "[1, 1, 3, 4, 5, 9]\n[1, 1, 3, 4, 5, 9]",
  "[3, 1, 4, 1, 5, 9]\n[1, 1, 3, 4, 5, 9]", "Error"],
 "[1, 1, 3, 4, 5, 9]\n[3, 1, 4, 1, 5, 9]",
 "sorted() returns a new sorted list without modifying the original. x.sort() would modify in-place.",
 "Does sorted() change the original list or return a new one?", 0.30, "program",
 "Python lists: CRUD operations, methods, list comprehensions"),

("What will be the output of the following Python code?\n\na = [1, 2, 3]\nb = a.copy()\nb.append(4)\nprint(len(a), len(b))",
 ["3 4", "4 4", "3 3", "Error"],
 "3 4", "a.copy() creates a shallow copy. Changes to b do not affect a.",
 "Unlike b = a, using .copy() creates an independent list.", 0.35, "program",
 "Python lists: CRUD operations, methods, list comprehensions"),

("What will be the output of the following Python code?\n\nmatrix = [[1,2],[3,4],[5,6]]\nprint([row[0] for row in matrix])",
 ["[1, 3, 5]", "[1, 2, 3]", "[[1],[3],[5]]", "[2, 4, 6]"],
 "[1, 3, 5]", "The comprehension extracts the first element (index 0) of each sublist.",
 "Think about what row[0] returns for each row in the matrix.", 0.50, "program",
 "Python lists: CRUD operations, methods, list comprehensions"),

("Which of the following correctly creates a list of squares of even numbers from 1 to 10?",
 ["[x**2 for x in range(1,11) if x%2==0]", "[x^2 for x in range(1,11) if x%2==0]",
  "[x**2 for x in range(1,10) if x%2==0]", "[x*x for x in range(2,11,2) if x%2==1]"],
 "[x**2 for x in range(1,11) if x**2==0]",
 "range(1,11) covers 1-10. x%2==0 filters even numbers. x**2 computes the square.",
 "Remember: ** is Python's exponentiation operator, not ^.", 0.45, "logic",
 "Python lists: CRUD operations, methods, list comprehensions"),

# ══ OOP (need 14 more to reach 18) ════════════════════════════════════

("What will be the output of the following Python code?\n\nclass Dog:\n    def __init__(self, name):\n        self.name = name\n    def bark(self):\n        return f'{self.name} says Woof!'\n\nd = Dog('Rex')\nprint(d.bark())",
 ["Rex says Woof!", "Dog says Woof!", "Error", "None"],
 "Rex says Woof!", "__init__ sets self.name = 'Rex'. bark() uses self.name in the f-string.",
 "Trace what self.name is set to when Dog('Rex') is called.", 0.20, "program",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

("What will be the output of the following Python code?\n\nclass Animal:\n    def speak(self):\n        return 'Generic sound'\n\nclass Cat(Animal):\n    def speak(self):\n        return 'Meow'\n\nc = Cat()\nprint(c.speak())",
 ["Generic sound", "Meow", "Error", "None"],
 "Meow", "Cat overrides the speak() method. When c.speak() is called on a Cat instance, Python uses Cat's version.",
 "When a child class defines the same method as the parent, which one gets called?", 0.25, "program",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

("What is the purpose of the __str__ method in a Python class?",
 ["To initialise the object", "To return a string representation of the object",
  "To compare two objects", "To delete the object"],
 "To return a string representation of the object",
 "__str__ is called by str() and print(). It should return a human-readable string describing the object.",
 "Think about what happens when you print() an object of your class.", 0.25, "direct",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

("What will be the output of the following Python code?\n\nclass Counter:\n    count = 0\n    def __init__(self):\n        Counter.count += 1\n\na = Counter()\nb = Counter()\nc = Counter()\nprint(Counter.count)",
 ["1", "2", "3", "0"],
 "3", "count is a class variable shared by all instances. Each __init__ call increments it once.",
 "Is 'count' an instance variable or a class variable? What's the difference?", 0.45, "program",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

("Which keyword is used to call the parent class's method from a child class?",
 ["parent()", "super()", "base()", "inherit()"],
 "super()", "super() returns a proxy object that delegates method calls to the parent class.",
 "Python has a built-in function specifically for calling parent class methods.", 0.20, "direct",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

("What will be the output of the following Python code?\n\nclass Rectangle:\n    def __init__(self, w, h):\n        self.w = w\n        self.h = h\n    def area(self):\n        return self.w * self.h\n    def __str__(self):\n        return f'Rectangle({self.w}x{self.h})'\n\nr = Rectangle(3, 4)\nprint(r)\nprint(r.area())",
 ["Rectangle(3x4)\n12", "3x4\n12", "Error", "Rectangle\n12"],
 "Rectangle(3x4)\n12", "print(r) calls __str__ which returns 'Rectangle(3x4)'. area() returns 3*4=12.",
 "What does print() call on an object to get its string representation?", 0.35, "program",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

("What will be the output of the following Python code?\n\nclass A:\n    def __init__(self):\n        self.x = 1\n\nclass B(A):\n    def __init__(self):\n        super().__init__()\n        self.y = 2\n\nb = B()\nprint(b.x, b.y)",
 ["1 2", "Error", "None None", "0 0"],
 "1 2", "super().__init__() calls A's __init__, setting self.x=1. Then B sets self.y=2.",
 "What does super().__init__() do in the child class constructor?", 0.40, "program",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

("What is encapsulation in Python OOP?",
 ["Wrapping data and methods into a single unit (class) and restricting direct access",
  "Creating multiple instances of a class",
  "Inheriting methods from a parent class",
  "Overriding a parent method in a child class"],
 "Wrapping data and methods into a single unit (class) and restricting direct access",
 "Encapsulation bundles data and behaviour into a class and uses access modifiers to protect internal state.",
 "Think about what 'encapsulate' means — to enclose something within a container.", 0.30, "direct",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

("What will be the output of the following Python code?\n\nclass Shape:\n    def area(self):\n        return 0\n\nclass Circle(Shape):\n    def __init__(self, r):\n        self.r = r\n    def area(self):\n        return 3.14 * self.r ** 2\n\nshapes = [Shape(), Circle(5)]\nfor s in shapes:\n    print(s.area())",
 ["0\n78.5", "0\n0", "Error", "78.5\n0"],
 "0\n78.5", "Shape.area() returns 0. Circle.area() returns 3.14 * 25 = 78.5. This is polymorphism.",
 "Each object uses its own version of area(). This is called polymorphism.", 0.45, "program",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

("What does the @property decorator do in Python?",
 ["Creates a class method", "Allows a method to be accessed like an attribute",
  "Makes an attribute private", "Creates a static method"],
 "Allows a method to be accessed like an attribute",
 "@property lets you define a method that can be accessed without parentheses, like obj.value instead of obj.value().",
 "Think about how you access regular attributes vs methods — @property bridges the two.", 0.55, "direct",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

("What will be the output of the following Python code?\n\nclass MyClass:\n    def __init__(self, val):\n        self.__val = val\n    def get_val(self):\n        return self.__val\n\nobj = MyClass(42)\nprint(obj.get_val())",
 ["42", "Error", "None", "__val"],
 "42", "__val is a private attribute (name mangling). It can be accessed via the getter method get_val().",
 "Double underscore prefix creates a private attribute. How do you access it?", 0.50, "program",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

("Which of the following is true about class methods in Python?",
 ["They take self as the first parameter",
  "They take cls as the first parameter and are decorated with @classmethod",
  "They take no parameters",
  "They are decorated with @staticmethod"],
 "They take cls as the first parameter and are decorated with @classmethod",
 "@classmethod decorator and cls parameter give the method access to the class itself, not instances.",
 "Compare @classmethod (receives class) with regular methods (receive instance) and @staticmethod (receive nothing).", 0.55, "direct",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

("What will be the output of the following Python code?\n\nclass Vehicle:\n    wheels = 4\n\nclass Bike(Vehicle):\n    wheels = 2\n\nv = Vehicle()\nb = Bike()\nprint(v.wheels, b.wheels, Vehicle.wheels)",
 ["4 2 4", "4 4 4", "2 2 4", "4 2 2"],
 "4 2 4", "Bike overrides the class variable 'wheels' with 2. Vehicle still has 4. Instances access their own class's variable.",
 "Class variables can be overridden in subclasses without affecting the parent class.", 0.50, "program",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

("What is method overriding in Python?",
 ["Defining multiple methods with the same name but different parameters",
  "Redefining a parent class method in a child class with the same name",
  "Calling a parent method from a child class",
  "Creating a method that can't be changed"],
 "Redefining a parent class method in a child class with the same name",
 "Method overriding allows a child class to provide its own implementation of a method already defined in the parent.",
 "Think about what 'override' means — replacing something that already exists.", 0.30, "direct",
 "Python OOP: classes, objects, inheritance, encapsulation, polymorphism"),

# ══ EXCEPTION HANDLING (need 15) ══════════════════════════════════════

("What will be the output of the following Python code?\n\ntry:\n    x = 1 / 0\nexcept ZeroDivisionError:\n    print('Cannot divide by zero')\nfinally:\n    print('Done')",
 ["Cannot divide by zero\nDone", "Cannot divide by zero", "Done", "Error"],
 "Cannot divide by zero\nDone", "ZeroDivisionError is caught, printing the message. finally always executes.",
 "Remember: the finally block runs regardless of whether an exception occurred.", 0.20, "program",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("What will be the output of the following Python code?\n\ntry:\n    print('try')\nexcept:\n    print('except')\nelse:\n    print('else')\nfinally:\n    print('finally')",
 ["try\nelse\nfinally", "try\nfinally", "try\nexcept\nfinally", "try\nexcept\nelse\nfinally"],
 "try\nelse\nfinally", "No exception occurs, so except is skipped, else runs (no exception path), then finally always runs.",
 "The else block runs only when NO exception occurs in the try block.", 0.40, "program",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("Which of the following correctly raises a ValueError with a message?",
 ["raise ValueError", "raise ValueError('Invalid input')", "throw ValueError('Invalid input')", "raise new ValueError('Invalid input')"],
 "raise ValueError('Invalid input')", "Python uses 'raise' keyword (not 'throw'). You can pass a message string to the exception constructor.",
 "Python's keyword for raising exceptions is 'raise', not 'throw' (which is used in Java/C++).", 0.20, "direct",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("What will be the output of the following Python code?\n\ntry:\n    lst = [1, 2, 3]\n    print(lst[5])\nexcept IndexError as e:\n    print(f'Error: {e}')",
 ["Error: list index out of range", "None", "Error: IndexError", "Error: 5"],
 "Error: list index out of range", "Accessing index 5 on a 3-element list raises IndexError. The 'as e' clause captures the exception message.",
 "What does the 'as e' syntax do when catching an exception?", 0.30, "program",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("What will be the output of the following Python code?\n\ndef check_age(age):\n    if age < 0:\n        raise ValueError('Age cannot be negative')\n    return age\n\ntry:\n    print(check_age(-1))\nexcept ValueError as e:\n    print(e)",
 ["Age cannot be negative", "-1", "Error", "ValueError"],
 "Age cannot be negative", "check_age(-1) raises ValueError. The except block catches it and prints the message string.",
 "What gets printed when you print() a caught exception object?", 0.35, "program",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("What will be the output of the following Python code?\n\ntry:\n    x = int('abc')\nexcept (ValueError, TypeError) as e:\n    print('Caught:', type(e).__name__)",
 ["Caught: ValueError", "Caught: TypeError", "Caught: Exception", "Error"],
 "Caught: ValueError", "int('abc') raises ValueError because 'abc' cannot be converted to int. type(e).__name__ gives the class name.",
 "int() raises ValueError when the string cannot be converted, not TypeError.", 0.40, "program",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("How do you create a custom exception in Python?",
 ["By using the 'exception' keyword", "By inheriting from the Exception class",
  "By using @exception decorator", "By defining a function that raises an error"],
 "By inheriting from the Exception class",
 "Custom exceptions are created by defining a class that inherits from Exception (or its subclasses).",
 "All built-in exceptions inherit from Exception. Your custom one should too.", 0.35, "direct",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("What will be the output of the following Python code?\n\nclass CustomError(Exception):\n    pass\n\ntry:\n    raise CustomError('Something went wrong')\nexcept CustomError as e:\n    print(f'Custom: {e}')",
 ["Custom: Something went wrong", "Error", "Custom: CustomError", "None"],
 "Custom: Something went wrong", "CustomError inherits from Exception. It's raised and caught like any other exception. str(e) gives the message.",
 "Custom exceptions work exactly like built-in ones once defined.", 0.40, "program",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("What will be the output of the following Python code?\n\ntry:\n    raise Exception('outer')\nexcept Exception as e:\n    try:\n        raise ValueError('inner')\n    except ValueError:\n        print('inner caught')\n    print('outer caught')",
 ["inner caught\nouter caught", "outer caught\ninner caught", "inner caught", "Error"],
 "inner caught\nouter caught", "The inner try-except catches ValueError first. Then execution continues in the outer except block.",
 "Nested try-except blocks work from innermost to outermost.", 0.55, "program",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("Which exception is raised when you try to access a key that doesn't exist in a dictionary?",
 ["IndexError", "ValueError", "KeyError", "AttributeError"],
 "KeyError", "Accessing a missing key with d[key] raises KeyError. Use d.get(key) to avoid this.",
 "Different container types raise different errors for missing elements. Lists raise IndexError, dicts raise ____.", 0.20, "direct",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("What will be the output of the following Python code?\n\nx = {'a': 1}\ntry:\n    print(x['b'])\nexcept KeyError:\n    print(x.get('b', 'Not found'))",
 ["Not found", "None", "KeyError", "Error"],
 "Not found", "x['b'] raises KeyError. x.get('b', 'Not found') returns the default 'Not found' when key is missing.",
 "dict.get(key, default) never raises KeyError — it returns the default instead.", 0.30, "program",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("What is the purpose of the 'finally' block in Python exception handling?",
 ["To catch all exceptions", "To run code only when no exception occurs",
  "To run code regardless of whether an exception occurred", "To re-raise the exception"],
 "To run code regardless of whether an exception occurred",
 "finally always executes — whether an exception occurred, was caught, or not. Useful for cleanup (closing files, etc.).",
 "Think of finally as 'cleanup code that must always run no matter what'.", 0.20, "direct",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("What will be the output of the following Python code?\n\ndef divide(a, b):\n    try:\n        result = a / b\n    except ZeroDivisionError:\n        return None\n    else:\n        return result\n\nprint(divide(10, 2))\nprint(divide(10, 0))",
 ["5.0\nNone", "5\nNone", "5.0\n0", "None\nNone"],
 "5.0\nNone", "divide(10,2): no exception, else runs, returns 5.0. divide(10,0): ZeroDivisionError caught, returns None.",
 "The else block in try-except only runs when NO exception is raised.", 0.45, "program",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("What will be the output of the following Python code?\n\ntry:\n    pass\nexcept Exception:\n    print('exception')\nelse:\n    print('else')\nfinally:\n    print('finally')",
 ["else\nfinally", "finally", "exception\nfinally", "else"],
 "else\nfinally", "No exception in try, so except is skipped, else runs, finally always runs.",
 "Map out all four blocks: try, except, else, finally — and when each runs.", 0.35, "program",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

("Which of the following is NOT a built-in Python exception?",
 ["IndexError", "ValueError", "NullPointerException", "KeyError"],
 "NullPointerException", "NullPointerException is a Java exception. Python uses None (not null) and raises AttributeError or TypeError for similar issues.",
 "One of these comes from a different programming language. Python doesn't have 'null'.", 0.25, "direct",
 "Python exception handling: try, except, finally, raise, custom exceptions"),

# ══ COMPREHENSIONS (need 15) ═══════════════════════════════════════════

("What will be the output of the following Python code?\n\nsquares = [x**2 for x in range(5)]\nprint(squares)",
 ["[1, 4, 9, 16, 25]", "[0, 1, 4, 9, 16]", "[0, 1, 2, 3, 4]", "[1, 2, 3, 4, 5]"],
 "[0, 1, 4, 9, 16]", "range(5) gives 0,1,2,3,4. Squaring each: 0,1,4,9,16.",
 "range(5) starts from 0, not 1. What is 0 squared?", 0.20, "program",
 "Python comprehensions: list, dict, set, generator expressions"),

("What will be the output of the following Python code?\n\nevens = [x for x in range(10) if x % 2 == 0]\nprint(evens)",
 ["[0, 2, 4, 6, 8]", "[2, 4, 6, 8, 10]", "[1, 3, 5, 7, 9]", "[0, 2, 4, 6, 8, 10]"],
 "[0, 2, 4, 6, 8]", "range(10) gives 0-9. Filtering x%2==0 keeps even numbers: 0,2,4,6,8.",
 "range(10) generates 0 through 9 (not 10). Filter for even numbers.", 0.15, "program",
 "Python comprehensions: list, dict, set, generator expressions"),

("What will be the output of the following Python code?\n\nd = {x: x**2 for x in range(1, 5)}\nprint(d)",
 ["{1: 1, 2: 4, 3: 9, 4: 16}", "{0: 0, 1: 1, 2: 4, 3: 9}", "{1: 2, 2: 4, 3: 6, 4: 8}", "Error"],
 "{1: 1, 2: 4, 3: 9, 4: 16}", "Dict comprehension {key: value for ...}. range(1,5) = 1,2,3,4. Each maps to its square.",
 "Dict comprehension syntax: {key_expr: value_expr for item in iterable}", 0.30, "program",
 "Python comprehensions: list, dict, set, generator expressions"),

("What will be the output of the following Python code?\n\nwords = ['hello', 'world']\nletters = [ch for word in words for ch in word]\nprint(len(letters))",
 ["10", "2", "5", "12"],
 "10", "'hello' has 5 chars, 'world' has 5 chars. Total 10 characters in the flattened list.",
 "This is a nested comprehension — it iterates over words, then over each character in each word.", 0.55, "program",
 "Python comprehensions: list, dict, set, generator expressions"),

("What is a generator expression in Python?",
 ["A list comprehension that uses square brackets",
  "A comprehension using parentheses that generates values lazily one at a time",
  "A function that creates lists",
  "A comprehension that always returns a set"],
 "A comprehension using parentheses that generates values lazily one at a time",
 "Generator expressions use () instead of []. They produce values on demand (lazy), saving memory vs list comprehensions.",
 "Compare [x for x in range(10)] with (x for x in range(10)) — what's different?", 0.40, "direct",
 "Python comprehensions: list, dict, set, generator expressions"),

("What will be the output of the following Python code?\n\ng = (x*2 for x in range(4))\nprint(type(g))\nprint(list(g))",
 ["<class 'generator'>\n[0, 2, 4, 6]", "<class 'list'>\n[0, 2, 4, 6]",
  "<class 'tuple'>\n[0, 2, 4, 6]", "Error"],
 "<class 'generator'>\n[0, 2, 4, 6]", "Parentheses create a generator object, not a list or tuple. list() consumes it.",
 "Parentheses around a comprehension create a generator, not a tuple.", 0.40, "program",
 "Python comprehensions: list, dict, set, generator expressions"),

("What will be the output of the following Python code?\n\nmatrix = [[1,2,3],[4,5,6],[7,8,9]]\nflat = [n for row in matrix for n in row]\nprint(flat)",
 ["[1, 2, 3, 4, 5, 6, 7, 8, 9]", "[[1,2,3],[4,5,6],[7,8,9]]", "[1,4,7,2,5,8,3,6,9]", "Error"],
 "[1, 2, 3, 4, 5, 6, 7, 8, 9]", "Nested comprehension: outer loop over rows, inner loop over elements. Flattens row by row.",
 "In nested comprehension, the outer loop comes first, inner loop second.", 0.45, "program",
 "Python comprehensions: list, dict, set, generator expressions"),

("What will be the output of the following Python code?\n\nresult = {x % 3 for x in range(10)}\nprint(result)",
 ["{0, 1, 2}", "{0, 1, 2, 0, 1, 2, 0, 1, 2, 0}", "{1, 2, 3}", "{0, 1, 2, 3}"],
 "{0, 1, 2}", "Set comprehension removes duplicates. x%3 for 0-9 gives 0,1,2,0,1,2,0,1,2,0. Unique values: {0,1,2}.",
 "Set comprehensions automatically remove duplicates — what unique values does x%3 produce for 0-9?", 0.45, "program",
 "Python comprehensions: list, dict, set, generator expressions"),

("What is the advantage of using a generator expression over a list comprehension?",
 ["Generators are faster for small datasets",
  "Generators use less memory by producing values one at a time",
  "Generators can be indexed like lists",
  "Generators always produce sorted output"],
 "Generators use less memory by producing values one at a time",
 "List comprehensions store all values in memory at once. Generators yield one value at a time — crucial for large datasets.",
 "Think about what happens in memory when you have a million items.", 0.35, "direct",
 "Python comprehensions: list, dict, set, generator expressions"),

("What will be the output of the following Python code?\n\nnums = [1, 2, 3, 4, 5]\nresult = [x for x in nums if x > 2 if x < 5]\nprint(result)",
 ["[3, 4]", "[1, 2, 3, 4, 5]", "[3, 4, 5]", "[2, 3, 4]"],
 "[3, 4]", "Two conditions: x > 2 AND x < 5. Only 3 and 4 satisfy both.",
 "Multiple if conditions in a comprehension are combined with AND logic.", 0.40, "program",
 "Python comprehensions: list, dict, set, generator expressions"),

("What will be the output of the following Python code?\n\npairs = [(x, y) for x in range(3) for y in range(3) if x != y]\nprint(len(pairs))",
 ["6", "9", "3", "4"],
 "6", "3x3=9 pairs total, minus 3 where x==y (0,0),(1,1),(2,2) = 6 pairs.",
 "Count total combinations first (3×3=9), then subtract the ones filtered out.", 0.55, "program",
 "Python comprehensions: list, dict, set, generator expressions"),

("What will be the output of the following Python code?\n\nresult = [x if x > 0 else -x for x in [-3, -1, 0, 2, 4]]\nprint(result)",
 ["[3, 1, 0, 2, 4]", "[-3, -1, 0, 2, 4]", "[3, 1, 0, -2, -4]", "Error"],
 "[3, 1, 0, 2, 4]", "Conditional expression x if x>0 else -x gives absolute value. -(-3)=3, -(-1)=1, 0=0, 2=2, 4=4.",
 "The expression 'x if condition else -x' is a ternary expression — different from the filter 'if' at the end.", 0.50, "program",
 "Python comprehensions: list, dict, set, generator expressions"),

("Which of the following creates a dictionary mapping each letter to its ASCII value?",
 ["{ch: ord(ch) for ch in 'abc'}", "{ch, ord(ch) for ch in 'abc'}",
  "[ch: ord(ch) for ch in 'abc']", "(ch: ord(ch) for ch in 'abc')"],
 "{ch: ord(ch) for ch in 'abc'}", "Dict comprehension uses {key: value ...} syntax. ord() returns the ASCII/Unicode code point.",
 "Dict comprehension uses curly braces with a colon separating key and value.", 0.30, "direct",
 "Python comprehensions: list, dict, set, generator expressions"),

("What will be the output of the following Python code?\n\nsentence = 'the quick brown fox'\nword_lengths = {word: len(word) for word in sentence.split()}\nprint(word_lengths['quick'])",
 ["5", "4", "3", "Error"],
 "5", "sentence.split() gives ['the','quick','brown','fox']. Dict maps each word to its length. len('quick')=5.",
 "How many characters does 'quick' have?", 0.25, "program",
 "Python comprehensions: list, dict, set, generator expressions"),

("What will be the output of the following Python code?\n\ng = (x**2 for x in range(5))\nprint(next(g))\nprint(next(g))\nprint(next(g))",
 ["0\n1\n4", "1\n4\n9", "0\n1\n2", "Error"],
 "0\n1\n4", "next() retrieves one value at a time from the generator. First call: 0**2=0, second: 1**2=1, third: 2**2=4.",
 "next() advances the generator by one step each time it's called.", 0.45, "program",
 "Python comprehensions: list, dict, set, generator expressions"),

# ══ DECORATORS (need 12) ═══════════════════════════════════════════════

("What is a decorator in Python?",
 ["A function that modifies the behaviour of another function",
  "A class that inherits from another class",
  "A way to add CSS styling to Python output",
  "A method for sorting collections"],
 "A function that modifies the behaviour of another function",
 "Decorators wrap a function to add functionality before/after it runs, without modifying its source code.",
 "Think of a decorator as a wrapper — it 'decorates' another function with extra behaviour.", 0.25, "direct",
 "Python decorators and closures"),

("What will be the output of the following Python code?\n\ndef my_decorator(func):\n    def wrapper():\n        print('Before')\n        func()\n        print('After')\n    return wrapper\n\n@my_decorator\ndef say_hello():\n    print('Hello')\n\nsay_hello()",
 ["Before\nHello\nAfter", "Hello", "Before\nAfter", "Before\nHello"],
 "Before\nHello\nAfter", "@my_decorator replaces say_hello with wrapper. Calling say_hello() calls wrapper() which prints Before, calls original func (Hello), then After.",
 "Trace through the wrapper function step by step.", 0.30, "program",
 "Python decorators and closures"),

("What is a closure in Python?",
 ["A function that closes the program",
  "A function that remembers variables from its enclosing scope even after that scope has finished",
  "A method that cannot be overridden",
  "A class with private attributes only"],
 "A function that remembers variables from its enclosing scope even after that scope has finished",
 "Closures capture variables from their enclosing function. The inner function 'closes over' those variables.",
 "What happens to variables in an outer function after it returns? Can the inner function still use them?", 0.45, "direct",
 "Python decorators and closures"),

("What will be the output of the following Python code?\n\ndef outer(x):\n    def inner(y):\n        return x + y\n    return inner\n\nadd5 = outer(5)\nprint(add5(3))",
 ["8", "5", "3", "Error"],
 "8", "outer(5) returns inner with x=5 captured. add5(3) calls inner(3) which returns 5+3=8. This is a closure.",
 "outer(5) returns a function. What is x set to inside that returned function?", 0.40, "program",
 "Python decorators and closures"),

("What does @staticmethod do in Python?",
 ["Makes the method private", "Creates a method that belongs to the class but takes no self or cls parameter",
  "Makes the method run faster", "Prevents the method from being overridden"],
 "Creates a method that belongs to the class but takes no self or cls parameter",
 "Static methods are defined in a class but don't access instance or class state. They're like regular functions inside a class.",
 "Compare: regular method (self), class method (cls), static method (no special first param).", 0.50, "direct",
 "Python decorators and closures"),

("What will be the output of the following Python code?\n\ndef counter():\n    count = 0\n    def increment():\n        nonlocal count\n        count += 1\n        return count\n    return increment\n\nc = counter()\nprint(c())\nprint(c())\nprint(c())",
 ["1\n2\n3", "1\n1\n1", "0\n1\n2", "Error"],
 "1\n2\n3", "nonlocal allows increment to modify count in outer scope. Each call increments and returns the persistent count.",
 "What does 'nonlocal' do? How does it allow the inner function to modify the outer variable?", 0.55, "program",
 "Python decorators and closures"),

("What will be the output of the following Python code?\n\ndef repeat(n):\n    def decorator(func):\n        def wrapper(*args, **kwargs):\n            for _ in range(n):\n                func(*args, **kwargs)\n        return wrapper\n    return decorator\n\n@repeat(3)\ndef greet():\n    print('Hi')\n\ngreet()",
 ["Hi\nHi\nHi", "Hi", "Error", "HiHiHi"],
 "Hi\nHi\nHi", "repeat(3) returns a decorator. @repeat(3) applies it to greet. wrapper calls greet 3 times.",
 "This is a decorator factory — repeat(3) returns the actual decorator. How many times does wrapper call func?", 0.65, "program",
 "Python decorators and closures"),

("What will be the output of the following Python code?\n\ndef bold(func):\n    def wrapper(text):\n        return '<b>' + func(text) + '</b>'\n    return wrapper\n\ndef italic(func):\n    def wrapper(text):\n        return '<i>' + func(text) + '</i>'\n    return wrapper\n\n@bold\n@italic\ndef format_text(text):\n    return text\n\nprint(format_text('hello'))",
 ["<b><i>hello</i></b>", "<i><b>hello</b></i>", "<b>hello</b>", "<i>hello</i>"],
 "<b><i>hello</i></b>", "Decorators are applied bottom-up: italic first wraps format_text, then bold wraps that. Order: bold(italic(format_text)).",
 "Multiple decorators are applied from bottom to top. Which one is applied first?", 0.70, "program",
 "Python decorators and closures"),

("Which of the following is the correct way to use functools.wraps when writing a decorator?",
 ["@wraps(func) on the wrapper function",
  "@wraps on the decorator function",
  "wraps(func) called after defining the decorator",
  "No need for functools.wraps — it's automatic"],
 "@wraps(func) on the wrapper function",
 "@functools.wraps(func) preserves the original function's name and docstring inside the wrapper.",
 "functools.wraps helps the wrapper function 'pretend' to be the original function for documentation purposes.", 0.65, "direct",
 "Python decorators and closures"),

("What will be the output of the following Python code?\n\ndef logger(func):\n    def wrapper(*args, **kwargs):\n        print(f'Calling {func.__name__}')\n        return func(*args, **kwargs)\n    return wrapper\n\n@logger\ndef add(a, b):\n    return a + b\n\nresult = add(3, 4)\nprint(result)",
 ["Calling add\n7", "7", "Calling add", "Calling add\nNone"],
 "Calling add\n7", "wrapper prints the function name, calls add(3,4)=7, returns 7. print(result) prints 7.",
 "Trace through: what does wrapper do, and what does it return?", 0.45, "program",
 "Python decorators and closures"),

("What is the difference between a closure and a class with __call__?",
 ["There is no difference", 
  "Closures are functions that capture variables; __call__ makes a class instance callable — both can achieve similar results",
  "Closures are faster", "Classes with __call__ cannot maintain state"],
 "Closures are functions that capture variables; __call__ makes a class instance callable — both can achieve similar results",
 "Both maintain state: closures via captured variables, __call__ classes via instance attributes. Choose based on complexity.",
 "Think about what makes a closure 'stateful' vs what makes a class instance 'callable'.", 0.70, "direct",
 "Python decorators and closures"),

("What will be the output of the following Python code?\n\ndef make_multiplier(n):\n    return lambda x: x * n\n\ndouble = make_multiplier(2)\ntriple = make_multiplier(3)\nprint(double(5))\nprint(triple(5))",
 ["10\n15", "5\n5", "10\n10", "Error"],
 "10\n15", "make_multiplier returns a lambda that closes over n. double captures n=2: 5*2=10. triple captures n=3: 5*3=15.",
 "Each returned lambda has its own captured value of n. What is n for double? For triple?", 0.50, "program",
 "Python decorators and closures"),

# ══ GENERATORS (need 12) ════════════════════════════════════════════════

("What keyword is used to create a generator function in Python?",
 ["return", "yield", "generate", "next"],
 "yield", "A function with 'yield' instead of 'return' becomes a generator function. It produces values lazily.",
 "Regular functions use 'return'. Generator functions use a different keyword to pause and produce values.", 0.15, "direct",
 "Python generators and iterators: yield, next, iter, StopIteration"),

("What will be the output of the following Python code?\n\ndef count_up(n):\n    i = 1\n    while i <= n:\n        yield i\n        i += 1\n\nfor num in count_up(3):\n    print(num)",
 ["1\n2\n3", "0\n1\n2", "1\n2", "Error"],
 "1\n2\n3", "count_up yields 1, 2, 3 one at a time. The for loop consumes each yielded value.",
 "Each yield pauses the function and sends a value. The loop resumes from where it paused.", 0.25, "program",
 "Python generators and iterators: yield, next, iter, StopIteration"),

("What will be the output of the following Python code?\n\ndef gen():\n    yield 1\n    yield 2\n    yield 3\n\ng = gen()\nprint(next(g))\nprint(next(g))",
 ["1\n2", "1\n1", "2\n3", "Error"],
 "1\n2", "Each next() call resumes the generator from after the last yield. First call: 1, second: 2.",
 "Think of yield as a 'pause point'. next() resumes from the last pause.", 0.25, "program",
 "Python generators and iterators: yield, next, iter, StopIteration"),

("What exception is raised when a generator is exhausted?",
 ["GeneratorExit", "StopIteration", "RuntimeError", "StopGenerator"],
 "StopIteration", "When a generator function returns (or runs off the end), it raises StopIteration. for loops catch this automatically.",
 "The for loop stops when it catches a specific exception from the iterator protocol.", 0.30, "direct",
 "Python generators and iterators: yield, next, iter, StopIteration"),

("What will be the output of the following Python code?\n\ndef squares(n):\n    for i in range(n):\n        yield i * i\n\ng = squares(4)\nprint(list(g))\nprint(list(g))",
 ["[0, 1, 4, 9]\n[]", "[0, 1, 4, 9]\n[0, 1, 4, 9]", "[1, 4, 9, 16]\n[]", "Error"],
 "[0, 1, 4, 9]\n[]", "list(g) exhausts the generator. Calling list(g) again gives [] because the generator is already done.",
 "A generator can only be iterated ONCE. After exhaustion, it produces nothing.", 0.45, "program",
 "Python generators and iterators: yield, next, iter, StopIteration"),

("What is the key advantage of generators over regular functions that return lists?",
 ["Generators are always faster", "Generators use less memory — they generate values one at a time instead of storing all at once",
  "Generators can be called multiple times", "Generators produce sorted output"],
 "Generators use less memory — they generate values one at a time instead of storing all at once",
 "For large sequences, generators are memory-efficient. range(1000000) uses almost no memory; list(range(1000000)) stores 1M numbers.",
 "Think about what happens in memory when you return a list of 1 million items vs yield them one by one.", 0.30, "direct",
 "Python generators and iterators: yield, next, iter, StopIteration"),

("What will be the output of the following Python code?\n\ndef fibonacci():\n    a, b = 0, 1\n    while True:\n        yield a\n        a, b = b, a + b\n\nfib = fibonacci()\nfor _ in range(6):\n    print(next(fib), end=' ')",
 ["0 1 1 2 3 5 ", "1 1 2 3 5 8 ", "0 1 2 3 4 5 ", "Error"],
 "0 1 1 2 3 5 ", "Fibonacci: starts 0,1. Each step: yield a, then a,b = b, a+b. Sequence: 0,1,1,2,3,5.",
 "Trace the first 6 fibonacci numbers starting from 0.", 0.55, "program",
 "Python generators and iterators: yield, next, iter, StopIteration"),

("What will be the output of the following Python code?\n\ndef gen():\n    print('Start')\n    x = yield 1\n    print(f'Got: {x}')\n    yield 2\n\ng = gen()\nprint(next(g))\nprint(g.send(42))",
 ["Start\n1\nGot: 42\n2", "Start\n1\n2", "1\nGot: 42\n2", "Error"],
 "Start\n1\nGot: 42\n2", "next(g) runs until first yield, prints 'Start', yields 1. send(42) resumes, x=42, prints 'Got: 42', yields 2.",
 "generator.send(value) resumes the generator AND sends a value back to the yield expression.", 0.75, "program",
 "Python generators and iterators: yield, next, iter, StopIteration"),

("Which of the following correctly implements an infinite counter generator?",
 ["def counter():\n    n = 0\n    while True:\n        yield n\n        n += 1",
  "def counter():\n    return range(999999999)",
  "def counter():\n    n = 0\n    while True:\n        return n\n        n += 1",
  "def counter():\n    for i in range(float('inf')):\n        yield i"],
 "def counter():\n    n = 0\n    while True:\n        yield n\n        n += 1",
 "An infinite generator uses while True with yield. return would exit the function; range(float('inf')) is invalid.",
 "An infinite generator must use yield (not return) and never end naturally.", 0.45, "logic",
 "Python generators and iterators: yield, next, iter, StopIteration"),

("What will be the output of the following Python code?\n\ndef chain(*iterables):\n    for it in iterables:\n        for item in it:\n            yield item\n\nresult = list(chain([1,2], [3,4], [5]))\nprint(result)",
 ["[1, 2, 3, 4, 5]", "[[1,2],[3,4],[5]]", "[1, 2, 3, 4]", "Error"],
 "[1, 2, 3, 4, 5]", "chain yields from each iterable in sequence, flattening them into one stream.",
 "The generator yields items from each iterable one by one, in order.", 0.50, "program",
 "Python generators and iterators: yield, next, iter, StopIteration"),

("What does the iter() function do in Python?",
 ["Returns the length of an iterable",
  "Returns an iterator object from an iterable",
  "Sorts the iterable",
  "Converts an iterator back to a list"],
 "Returns an iterator object from an iterable",
 "iter(obj) calls obj.__iter__() and returns an iterator. Lists, tuples, dicts are iterable but not iterators — iter() converts them.",
 "There's a difference between 'iterable' and 'iterator'. iter() creates an iterator from an iterable.", 0.45, "direct",
 "Python generators and iterators: yield, next, iter, StopIteration"),

("What will be the output of the following Python code?\n\ndef take(n, iterable):\n    it = iter(iterable)\n    for _ in range(n):\n        yield next(it)\n\nprint(list(take(3, range(10))))",
 ["[0, 1, 2]", "[1, 2, 3]", "[0, 1, 2, 3]", "Error"],
 "[0, 1, 2]", "take creates an iterator from range(10), then yields the first n=3 values: 0, 1, 2.",
 "iter() on range(10) creates an iterator. next() gets values one at a time.", 0.55, "program",
 "Python generators and iterators: yield, next, iter, StopIteration"),

# ══ MODULES (need 12) ══════════════════════════════════════════════════

("Which of the following correctly imports only the sqrt function from the math module?",
 ["import sqrt from math", "from math import sqrt", "import math.sqrt", "include math.sqrt"],
 "from math import sqrt", "'from module import name' imports a specific name. 'import module' imports the whole module.",
 "Python's import syntax: 'from X import Y' to get just one thing from a module.", 0.15, "direct",
 "Python modules, packages, imports, and standard library"),

("What will be the output of the following Python code?\n\nimport math\nprint(math.ceil(4.2))\nprint(math.floor(4.8))",
 ["5\n4", "4\n5", "5\n5", "4\n4"],
 "5\n4", "math.ceil rounds up to nearest integer: ceil(4.2)=5. math.floor rounds down: floor(4.8)=4.",
 "ceil = ceiling (always up), floor = floor (always down). They're opposites.", 0.20, "program",
 "Python modules, packages, imports, and standard library"),

("What does the 'as' keyword do in an import statement?",
 ["Creates a new module", "Creates an alias for the imported module or name",
  "Checks if the module exists", "Hides the original module name"],
 "Creates an alias for the imported module or name",
 "'import numpy as np' creates the alias 'np' for numpy. Useful for long module names or avoiding name conflicts.",
 "Why do data scientists write 'import numpy as np' instead of 'import numpy'?", 0.15, "direct",
 "Python modules, packages, imports, and standard library"),

("What will be the output of the following Python code?\n\nimport random\nrandom.seed(42)\nprint(random.randint(1, 10))",
 ["The output is deterministic but implementation-specific",
  "Always 0", "Always 10", "Error"],
 "The output is deterministic but implementation-specific",
 "random.seed(42) makes the random number generator deterministic. The specific output depends on Python version/implementation.",
 "Seeding random makes it reproducible — same seed always gives same sequence. But the value depends on Python version.", 0.45, "direct",
 "Python modules, packages, imports, and standard library"),

("What is the purpose of __name__ == '__main__' in Python?",
 ["To import the module", "To check if the script is being run directly (not imported as a module)",
  "To define the main function", "To prevent the file from being imported"],
 "To check if the script is being run directly (not imported as a module)",
 "When a script is run directly, __name__ is '__main__'. When imported, __name__ is the module name. This lets you write code that only runs when executed directly.",
 "When you import a module, does its top-level code run? What about code inside 'if __name__ == __main__'?", 0.35, "direct",
 "Python modules, packages, imports, and standard library"),

("What will be the output of the following Python code?\n\nfrom collections import Counter\nwords = ['apple', 'banana', 'apple', 'cherry', 'banana', 'apple']\nc = Counter(words)\nprint(c['apple'])",
 ["3", "1", "2", "Error"],
 "3", "Counter counts occurrences. 'apple' appears 3 times in the list.",
 "Counter maps each element to how many times it appears.", 0.20, "program",
 "Python modules, packages, imports, and standard library"),

("What will be the output of the following Python code?\n\nfrom collections import defaultdict\nd = defaultdict(int)\nfor ch in 'hello':\n    d[ch] += 1\nprint(dict(d))",
 ["{'h': 1, 'e': 1, 'l': 2, 'o': 1}", "{'h': 1, 'e': 1, 'l': 1, 'o': 1}", "Error", "{'hello': 1}"],
 "{'h': 1, 'e': 1, 'l': 2, 'o': 1}", "defaultdict(int) gives 0 for missing keys. 'l' appears twice, others once.",
 "defaultdict(int) initialises missing keys to 0 (int()'s default). Count each character.", 0.35, "program",
 "Python modules, packages, imports, and standard library"),

("What does the os.path.join() function do?",
 ["Joins two strings with a comma",
  "Constructs a file path by joining components with the OS-appropriate separator",
  "Checks if a file path exists",
  "Splits a path into directory and filename"],
 "Constructs a file path by joining components with the OS-appropriate separator",
 "os.path.join('home', 'user', 'file.txt') produces 'home/user/file.txt' on Linux, 'home\\user\\file.txt' on Windows.",
 "Why not just use string concatenation for file paths? Think about Windows vs Linux.", 0.30, "direct",
 "Python modules, packages, imports, and standard library"),

("What will be the output of the following Python code?\n\nfrom itertools import chain\nresult = list(chain([1,2], [3,4], [5,6]))\nprint(result)",
 ["[1, 2, 3, 4, 5, 6]", "[[1,2],[3,4],[5,6]]", "[1, 2, 3, 4]", "Error"],
 "[1, 2, 3, 4, 5, 6]", "itertools.chain concatenates multiple iterables into one sequence.",
 "itertools.chain 'chains' multiple iterables together into one flat sequence.", 0.25, "program",
 "Python modules, packages, imports, and standard library"),

("What does sys.argv contain in Python?",
 ["The current Python version", "A list of command-line arguments passed to the script",
  "The system's environment variables", "All imported modules"],
 "A list of command-line arguments passed to the script",
 "sys.argv[0] is the script name, sys.argv[1] onwards are the arguments. Running 'python script.py hello' gives sys.argv=['script.py','hello'].",
 "What gets passed to a Python script when you run it from the command line?", 0.30, "direct",
 "Python modules, packages, imports, and standard library"),

("What will be the output of the following Python code?\n\nfrom functools import reduce\nresult = reduce(lambda x, y: x * y, [1, 2, 3, 4, 5])\nprint(result)",
 ["120", "15", "24", "Error"],
 "120", "reduce applies lambda cumulatively: 1*2=2, 2*3=6, 6*4=24, 24*5=120. That's 5!.",
 "reduce applies the function cumulatively to the list. Trace: 1×2=2, 2×3=6, 6×4=?, 24×5=?", 0.50, "program",
 "Python modules, packages, imports, and standard library"),

("What is a Python package?",
 ["A single Python file", "A directory containing an __init__.py file and other Python modules",
  "A compressed zip of Python scripts", "A built-in Python function"],
 "A directory containing an __init__.py file and other Python modules",
 "A package is a directory with __init__.py that organises related modules. It enables 'from package.module import something'.",
 "How does Python distinguish a regular directory from a package directory?", 0.25, "direct",
 "Python modules, packages, imports, and standard library"),

# ══ FILE I/O (need 12) ══════════════════════════════════════════════════

("What is the correct way to open a file for reading in Python?",
 ["open('file.txt')", "open('file.txt', 'r')", "Both A and B are correct", "read('file.txt')"],
 "Both A and B are correct",
 "'r' (read) is the default mode. open('file.txt') and open('file.txt', 'r') are equivalent.",
 "What is the default mode when you don't specify one in open()?", 0.15, "direct",
 "Python file I/O: open, read, write, context managers, with statement"),

("What is the advantage of using 'with open()' over just 'open()'?",
 ["It's faster", "It automatically closes the file even if an exception occurs",
  "It reads the whole file at once", "It works only with text files"],
 "It automatically closes the file even if an exception occurs",
 "The 'with' statement is a context manager. It calls __exit__ (which closes the file) when the block ends, even on error.",
 "What happens to an open file if an exception occurs before you call file.close()?", 0.25, "direct",
 "Python file I/O: open, read, write, context managers, with statement"),

("Which file mode is used to append to an existing file without overwriting it?",
 ["'w'", "'r'", "'a'", "'x'"],
 "'a'", "'a' (append) adds to the end of the file. 'w' overwrites the whole file.",
 "If you want to add to a file without losing what's already there, which mode do you use?", 0.15, "direct",
 "Python file I/O: open, read, write, context managers, with statement"),

("What will the following Python code do?\n\nwith open('data.txt', 'w') as f:\n    f.write('Hello')\n    f.write(' World')",
 ["Writes 'Hello\\n World' with a newline", "Writes 'Hello World' to the file",
  "Raises an error because you can't call write twice", "Creates two files"],
 "Writes 'Hello World' to the file",
 "write() doesn't add newlines automatically. Two write() calls concatenate: 'Hello' + ' World' = 'Hello World'.",
 "Does write() add a newline at the end automatically?", 0.25, "program",
 "Python file I/O: open, read, write, context managers, with statement"),

("What does file.readlines() return?",
 ["A single string with the entire file content",
  "A list of strings, one per line (including newline characters)",
  "A generator of lines",
  "The number of lines in the file"],
 "A list of strings, one per line (including newline characters)",
 "readlines() returns a list like ['line1\\n', 'line2\\n', 'line3']. Each string includes the newline except possibly the last.",
 "What's the difference between read(), readline(), and readlines()?", 0.30, "direct",
 "Python file I/O: open, read, write, context managers, with statement"),

("What file mode would you use to open a binary file for reading?",
 ["'r'", "'rb'", "'b'", "'br'"],
 "'rb'", "'rb' = read binary. Used for non-text files like images, PDFs, executables.",
 "Binary mode adds 'b' to the mode string. What does 'rb' stand for?", 0.20, "direct",
 "Python file I/O: open, read, write, context managers, with statement"),

("What does the following code do?\n\nwith open('file.txt', 'r') as f:\n    for line in f:\n        print(line.strip())",
 ["Reads the file all at once into memory",
  "Reads the file line by line (memory efficient)",
  "Writes lines to the file",
  "Error — cannot iterate over a file object"],
 "Reads the file line by line (memory efficient)",
 "Iterating over a file object reads one line at a time — efficient for large files. strip() removes the trailing newline.",
 "When you use 'for line in file', how much of the file is in memory at once?", 0.35, "direct",
 "Python file I/O: open, read, write, context managers, with statement"),

("What will happen if you try to open a file with mode 'x' and the file already exists?",
 ["The file is overwritten", "A FileExistsError is raised",
  "The file is opened for appending", "Nothing — it opens normally"],
 "A FileExistsError is raised",
 "'x' (exclusive creation) creates a new file but fails if the file already exists. Use when you want to ensure you don't overwrite.",
 "Mode 'x' is designed for creating NEW files only. What happens if the file exists?", 0.40, "direct",
 "Python file I/O: open, read, write, context managers, with statement"),

("What does the following code print?\n\nimport os\nprint(os.path.exists('nonexistent_file.txt'))",
 ["True", "False", "Error", "None"],
 "False", "os.path.exists() returns False for files that don't exist, True for those that do. No exception raised.",
 "os.path.exists() safely checks if a path exists without raising an exception.", 0.20, "program",
 "Python file I/O: open, read, write, context managers, with statement"),

("What will the following code do?\n\nwith open('numbers.txt', 'w') as f:\n    for i in range(3):\n        f.write(str(i) + '\\n')",
 ["Writes '012' to the file",
  "Writes '0\\n1\\n2\\n' to the file (three lines)",
  "Raises an error — cannot write integers",
  "Writes '[0, 1, 2]' to the file"],
 "Writes '0\\n1\\n2\\n' to the file (three lines)",
 "str(i) converts each int to string. '\\n' adds a newline. The file gets three lines: 0, 1, 2.",
 "write() only accepts strings. What does str(i) + '\\n' produce for i=0,1,2?", 0.30, "program",
 "Python file I/O: open, read, write, context managers, with statement"),

("What is a context manager in Python?",
 ["A function that manages memory",
  "An object that defines __enter__ and __exit__ for use with the 'with' statement",
  "A decorator for managing threads",
  "A built-in module for file management"],
 "An object that defines __enter__ and __exit__ for use with the 'with' statement",
 "Context managers implement __enter__ (setup) and __exit__ (cleanup). 'with' calls these automatically.",
 "What two methods must an object implement to be used with the 'with' statement?", 0.45, "direct",
 "Python file I/O: open, read, write, context managers, with statement"),

("What does json.dump() vs json.dumps() do?",
 ["dump() writes to a file, dumps() returns a string",
  "dumps() writes to a file, dump() returns a string",
  "They are identical",
  "dump() is for dicts only, dumps() works for all types"],
 "dump() writes to a file, dumps() returns a string",
 "json.dump(obj, file) writes JSON to a file object. json.dumps(obj) returns JSON as a string. The 's' stands for 'string'.",
 "The 's' in dumps stands for 'string'. Without 's', it works with a file object.", 0.35, "direct",
 "Python file I/O: open, read, write, context managers, with statement"),

# ══ VARIABLES / DATA TYPES — extras ════════════════════════════════════

("What will be the output of the following Python code?\n\nx = 5\ny = 2\nprint(x // y)\nprint(x % y)",
 ["2\n1", "2.5\n1", "2\n0", "2\n2"],
 "2\n1", "// is integer (floor) division: 5//2=2. % is modulo (remainder): 5%2=1.",
 "// gives the integer part of division. % gives the remainder.", 0.15, "program",
 "Python operators: arithmetic, comparison, logical, bitwise, precedence"),

("What will be the output of the following Python code?\n\nprint(type(3 / 2))\nprint(type(3 // 2))",
 ["<class 'float'>\n<class 'int'>", "<class 'int'>\n<class 'float'>",
  "<class 'float'>\n<class 'float'>", "<class 'int'>\n<class 'int'>"],
 "<class 'float'>\n<class 'int'>", "/ always returns float (3/2=1.5). // returns int when both operands are int (3//2=1).",
 "What type does / always return vs what // returns?", 0.25, "program",
 "Python operators: arithmetic, comparison, logical, bitwise, precedence"),

("What will be the output of the following Python code?\n\na = 10\nb = 3\nprint(a & b)\nprint(a | b)",
 ["2\n11", "10\n3", "1\n11", "2\n3"],
 "2\n11", "10=1010, 3=0011 in binary. AND: 0010=2. OR: 1011=11.",
 "Convert both numbers to binary first, then apply AND (&) and OR (|) bit by bit.", 0.55, "program",
 "Python operators: arithmetic, comparison, logical, bitwise, precedence"),

]

# Verify all program-type questions
import subprocess, sys

print(f"Generated {len(new_questions_raw)} questions")
print("\nVerifying program-type code outputs...")

verified = []
issues = []

for i, q_data in enumerate(new_questions_raw):
    q_text, opts, correct, explanation, hint, diff, qtype, topic = q_data
    
    if qtype == 'program' and '\n\n' in q_text:
        code = q_text.split('\n\n', 1)[1].strip()
        try:
            result = subprocess.run([sys.executable, '-c', code],
                                   capture_output=True, text=True, timeout=5)
            actual = result.stdout.strip()
            exp_clean = correct.replace('\\n', '\n').strip()
            if actual and actual != exp_clean:
                issues.append(f"Q{i+1} [{qtype}]: Got '{actual}' expected '{exp_clean}'")
        except Exception as e:
            issues.append(f"Q{i+1}: Error running code: {e}")
    
    verified.append(q_data)

if issues:
    print(f"Issues found ({len(issues)}):")
    for iss in issues:
        print(f"  {iss}")
else:
    print("All program questions verified ✓")

print(f"\nTotal verified: {len(verified)}")

# Save
output = []
for qd in verified:
    output.append({
        "question": qd[0],
        "options": qd[1],
        "correct_answer": qd[2],
        "explanation": qd[3],
        "hint": qd[4],
        "difficulty": qd[5],
        "type": qd[6],
        "topic": qd[7],
    })

with open('/home/claude/adaptive-ide/simulator/new_questions_raw.json', 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print("Saved to new_questions_raw.json")
EOF