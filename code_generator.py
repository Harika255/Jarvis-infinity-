import re


def _normalize(question):
    return re.sub(r"\s+", " ", question.strip().lower())


def _python(question):
    q = _normalize(question)

    if "factorial" in q:
        code = """def factorial(n):
    if n < 0:
        return "Factorial is not defined for negative numbers"
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


number = int(input("Enter a number: "))
print("Factorial:", factorial(number))
"""
        title = "Python Factorial Program"
        return code, title

    if "prime" in q:
        code = """def is_prime(n):
    if n <= 1:
        return False

    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False

    return True


number = int(input("Enter a number: "))

if is_prime(number):
    print(number, "is a prime number")
else:
    print(number, "is not a prime number")
"""
        title = "Python Prime Number Checker"
        return code, title

    if "palindrome" in q:
        code = """text = input("Enter a string: ")

if text == text[::-1]:
    print("The string is a palindrome")
else:
    print("The string is not a palindrome")
"""
        title = "Python Palindrome Checker"
        return code, title

    if "reverse" in q and "string" in q:
        code = """text = input("Enter a string: ")

reversed_text = text[::-1]

print("Reversed string:", reversed_text)
"""
        title = "Python String Reversal"
        return code, title

    if "fibonacci" in q:
        code = """n = int(input("Enter the number of terms: "))

a = 0
b = 1

print("Fibonacci sequence:")

for i in range(n):
    print(a, end=" ")
    a, b = b, a + b
"""
        title = "Python Fibonacci Series"
        return code, title

    if "largest" in q and "three" in q:
        code = """numbers = []

for i in range(3):
    number = int(input(f"Enter number {i + 1}: "))
    numbers.append(number)

numbers.sort(reverse=True)

print("Largest number:", numbers[0])
"""
        title = "Python Largest of Three Numbers"
        return code, title

    if "even" in q and "odd" in q:
        code = """number = int(input("Enter a number: "))

if number % 2 == 0:
    print("The number is even")
else:
    print("The number is odd")
"""
        title = "Python Even or Odd Checker"
        return code, title

    if "calculator" in q:
        code = """num1 = float(input("Enter first number: "))
operator = input("Enter operator (+, -, *, /): ")
num2 = float(input("Enter second number: "))

if operator == "+":
    result = num1 + num2
elif operator == "-":
    result = num1 - num2
elif operator == "*":
    result = num1 * num2
elif operator == "/":
    if num2 == 0:
        result = "Cannot divide by zero"
    else:
        result = num1 / num2
else:
    result = "Invalid operator"

print("Result:", result)
"""
        title = "Python Calculator"
        return code, title

    if "sum" in q and "list" in q:
        code = """numbers = list(map(int, input("Enter numbers separated by spaces: ").split()))

total = sum(numbers)

print("Sum:", total)
"""
        title = "Python List Sum Program"
        return code, title

    if "sort" in q and "list" in q:
        code = """numbers = list(map(int, input("Enter numbers separated by spaces: ").split()))

numbers.sort()

print("Sorted list:", numbers)
"""
        title = "Python List Sorting Program"
        return code, title

    safe_question = question.replace('"', '\\"')

    code = """# JARVIS generated Python program

# User request:
# QUESTION_PLACEHOLDER

def main():
    print("JARVIS generated this Python program.")
    print("Modify this starter code according to your requirements.")


if __name__ == "__main__":
    main()
"""

    code = code.replace("QUESTION_PLACEHOLDER", safe_question)

    title = "Python Generated Program"

    return code, title


def _java(question):
    q = _normalize(question)

    if "factorial" in q:
        body = """        int number = 5;
        long factorial = 1;

        for (int i = 1; i <= number; i++) {
            factorial *= i;
        }

        System.out.println("Factorial: " + factorial);"""

        title = "Java Factorial Program"

    elif "prime" in q:
        body = """        int number = 29;
        boolean prime = true;

        if (number <= 1) {
            prime = false;
        }

        for (int i = 2; i <= Math.sqrt(number); i++) {
            if (number % i == 0) {
                prime = false;
                break;
            }
        }

        if (prime) {
            System.out.println(number + " is a prime number");
        } else {
            System.out.println(number + " is not a prime number");
        }"""

        title = "Java Prime Number Checker"

    elif "largest" in q and "three" in q:
        body = """        int a = 10;
        int b = 25;
        int c = 15;

        int largest = Math.max(a, Math.max(b, c));

        System.out.println("Largest number: " + largest);"""

        title = "Java Largest of Three Numbers"

    elif "palindrome" in q:
        body = """        String text = "madam";
        String reversed = new StringBuilder(text).reverse().toString();

        if (text.equals(reversed)) {
            System.out.println("The string is a palindrome");
        } else {
            System.out.println("The string is not a palindrome");
        }"""

        title = "Java Palindrome Checker"

    elif "fibonacci" in q:
        body = """        int n = 10;
        int a = 0;
        int b = 1;

        System.out.println("Fibonacci sequence:");

        for (int i = 0; i < n; i++) {
            System.out.print(a + " ");
            int next = a + b;
            a = b;
            b = next;
        }"""

        title = "Java Fibonacci Series"

    elif "even" in q and "odd" in q:
        body = """        int number = 10;

        if (number % 2 == 0) {
            System.out.println("The number is even");
        } else {
            System.out.println("The number is odd");
        }"""

        title = "Java Even or Odd Checker"

    else:
        safe_question = question.replace('"', '\\"')

        body = """        System.out.println("JARVIS generated a Java program.");
        System.out.println("Request: QUESTION_PLACEHOLDER");"""

        body = body.replace("QUESTION_PLACEHOLDER", safe_question)

        title = "Java Generated Program"

    code = (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        + body
        + "\n"
        "    }\n"
        "}\n"
    )

    return code, title


def _javascript(question):
    q = _normalize(question)

    if "factorial" in q:
        code = """function factorial(n) {
    let result = 1;

    for (let i = 1; i <= n; i++) {
        result *= i;
    }

    return result;
}

const number = 5;

console.log("Factorial:", factorial(number));
"""
        title = "JavaScript Factorial Program"
        return code, title

    if "prime" in q:
        code = """function isPrime(n) {
    if (n <= 1) {
        return false;
    }

    for (let i = 2; i <= Math.sqrt(n); i++) {
        if (n % i === 0) {
            return false;
        }
    }

    return true;
}

const number = 29;

if (isPrime(number)) {
    console.log(number + " is a prime number");
} else {
    console.log(number + " is not a prime number");
}
"""
        title = "JavaScript Prime Number Checker"
        return code, title

    if "background" in q and "button" in q:
        code = """const button = document.querySelector("button");

button.addEventListener("click", function () {
    document.body.style.backgroundColor = "lightblue";
});
"""
        title = "JavaScript Button Background Changer"
        return code, title

    if "button" in q and "click" in q:
        code = """const button = document.querySelector("#myButton");

button.addEventListener("click", function () {
    alert("Button clicked!");
});
"""
        title = "JavaScript Button Click Event"
        return code, title

    if "reverse" in q and "string" in q:
        code = """function reverseString(text) {
    return text.split("").reverse().join("");
}

const text = "JARVIS";

console.log("Reversed:", reverseString(text));
"""
        title = "JavaScript String Reversal"
        return code, title

    safe_question = question.replace("*/", "* /")

    code = """// JARVIS generated JavaScript program

/*
User request:
QUESTION_PLACEHOLDER
*/

function main() {
    console.log("JARVIS generated this JavaScript program.");
}

main();
"""

    code = code.replace("QUESTION_PLACEHOLDER", safe_question)

    title = "JavaScript Generated Program"

    return code, title


def _html(question):
    q = _normalize(question)

    if "login" in q:
        code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS Login</title>
</head>
<body>

    <h1>Login</h1>

    <form>
        <label>Email:</label>
        <input type="email" placeholder="Enter your email">

        <br><br>

        <label>Password:</label>
        <input type="password" placeholder="Enter your password">

        <br><br>

        <button type="submit">Login</button>
    </form>

</body>
</html>
"""
        title = "HTML Login Page"
        return code, title

    if "form" in q or "registration" in q:
        code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registration Form</title>
</head>
<body>

    <h1>Registration Form</h1>

    <form>
        <label>Name:</label>
        <input type="text" placeholder="Enter your name">

        <br><br>

        <label>Email:</label>
        <input type="email" placeholder="Enter your email">

        <br><br>

        <label>Password:</label>
        <input type="password" placeholder="Enter your password">

        <br><br>

        <button type="submit">Register</button>
    </form>

</body>
</html>
"""
        title = "HTML Registration Form"
        return code, title

    if "table" in q:
        code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Table</title>
</head>
<body>

    <h1>Student Details</h1>

    <table border="1">
        <tr>
            <th>Name</th>
            <th>Branch</th>
            <th>Year</th>
        </tr>

        <tr>
            <td>Student 1</td>
            <td>CSE</td>
            <td>2nd Year</td>
        </tr>

        <tr>
            <td>Student 2</td>
            <td>CSE</td>
            <td>2nd Year</td>
        </tr>
    </table>

</body>
</html>
"""
        title = "HTML Student Table"
        return code, title

    if "portfolio" in q:
        code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Portfolio</title>
</head>
<body>

    <header>
        <h1>My Portfolio</h1>
        <p>Computer Science Engineering Student</p>
    </header>

    <section>
        <h2>About Me</h2>
        <p>Welcome to my portfolio.</p>
    </section>

    <section>
        <h2>Skills</h2>
        <ul>
            <li>Python</li>
            <li>Java</li>
            <li>HTML</li>
            <li>CSS</li>
            <li>JavaScript</li>
        </ul>
    </section>

</body>
</html>
"""
        title = "HTML Portfolio Website"
        return code, title

    safe_question = (
        question
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS Generated Page</title>
</head>
<body>

    <h1>JARVIS Generated HTML</h1>

    <p>Requested feature:</p>

    <p>QUESTION_PLACEHOLDER</p>

</body>
</html>
"""

    code = code.replace("QUESTION_PLACEHOLDER", safe_question)

    title = "HTML Generated Page"

    return code, title


def _css(question):
    q = _normalize(question)

    if "card" in q:
        code = """body {
    font-family: Arial, sans-serif;
    background: #f4f7fb;
}

.card {
    width: 300px;
    padding: 25px;
    margin: 50px auto;
    background: white;
    border-radius: 15px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
}

.card h2 {
    margin-bottom: 10px;
}
"""
        title = "CSS Card Design"
        return code, title

    if "button" in q:
        code = """button {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    background: #6c63ff;
    color: white;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    opacity: 0.85;
}
"""
        title = "CSS Button Design"
        return code, title

    if "responsive" in q:
        code = """body {
    margin: 0;
    font-family: Arial, sans-serif;
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: auto;
}

@media (max-width: 768px) {
    .container {
        width: 95%;
    }
}
"""
        title = "Responsive CSS Layout"
        return code, title

    safe_question = question.replace("*/", "* /")

    code = """/* JARVIS generated CSS */

/*
User request:
QUESTION_PLACEHOLDER
*/

body {
    font-family: Arial, sans-serif;
}

.container {
    max-width: 1200px;
    margin: auto;
    padding: 20px;
}
"""

    code = code.replace("QUESTION_PLACEHOLDER", safe_question)

    title = "CSS Generated Layout"

    return code, title


def generate_code(question, language):
    if not question or not question.strip():
        return {
            "language": language,
            "title": "No Question",
            "code": "",
            "explanation": "Please enter a coding question."
        }

    language = language.strip().lower()

    if language == "auto detect":
        question_lower = question.lower()

        if "html" in question_lower or "web page" in question_lower:
            language = "html"
        elif "css" in question_lower or "style" in question_lower:
            language = "css"
        elif "javascript" in question_lower or "js" in question_lower:
            language = "javascript"
        elif "java" in question_lower:
            language = "java"
        else:
            language = "python"

    if language == "python":
        code, title = _python(question)

    elif language == "java":
        code, title = _java(question)

    elif language in ["javascript", "js"]:
        language = "javascript"
        code, title = _javascript(question)

    elif language == "html":
        code, title = _html(question)

    elif language == "css":
        code, title = _css(question)

    else:
        language = "python"
        code, title = _python(question)

    explanation = (
        "JARVIS analyzed the user's question and generated "
        + language.title()
        + " code based on the detected requirement."
    )

    return {
        "language": language,
        "title": title,
        "code": code,
        "explanation": explanation
    }