## Question ID : DSA-0001
**Question**

What is a data structure?

**Options**

A) A programming language
B) A collection of algorithms
C) A way to store and organize data
D) A type of computer hardware

**Correct Answer**

A way to store and organize data

**Explanation**

A data structure is a way to store and organize data efficiently, enhancing access and manipulation, unlike programming languages, algorithms, or computer hardware.

**Difficulty (0.0 – 1.0)**

0.1

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0002
**Question**

What are the disadvantages of arrays?

**Options**

A) Index value of an array can be negative
B) Elements are sequentially accessed
C) Data structure like queue or stack cannot be implemented
D) There are chances of wastage of memory space if elements inserted in an array are lesser than the allocated size

**Correct Answer**

There are chances of wastage of memory space if elements inserted in an array are lesser than the allocated size

**Explanation**

Arrays are of fixed size. If we insert elements less than the allocated size, unoccupied positions can’t be used again. Wastage will occur in memory.

**Difficulty (0.0 – 1.0)**

0.2

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0003
**Question**

Which data structure is used for implementing recursion?

**Options**

A) Stack
B) Queue
C) List
D) Array

**Correct Answer**

Stack

**Explanation**

Stacks are used for the implementation of Recursion.

**Difficulty (0.0 – 1.0)**

0.2

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0004
**Question**

The data structure required to check whether an expression contains a balanced parenthesis is?

**Options**

A) Queue
B) Stack
C) Tree
D) Array

**Correct Answer**

Stack

**Explanation**

The stack is a simple data structure in which elements are added and removed based on the LIFO principle. Open parenthesis is pushed into the stack and a closed parenthesis pops out elements till the top element of the stack is its corresponding open parenthesis. If the stack is empty, parenthesis is balanced otherwise it is unbalanced.

**Difficulty (0.0 – 1.0)**

0.3

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0005
**Question**

Which of the following is not the application of stack?

**Options**

A) Data Transfer between two asynchronous process
B) Compiler Syntax Analyzer
C) Tracking of local variables at run time
D) A parentheses balancing program

**Correct Answer**

Data Transfer between two asynchronous process

**Explanation**

Data transfer between the two asynchronous process uses the queue data structure for synchronisation. The rest are all stack applications.

**Difficulty (0.0 – 1.0)**

0.35

**Type**

logic

**Estimated Time (seconds)**

50

---

## Question ID : DSA-0006
**Question**

Which data structure is needed to convert infix notation to postfix notation?

**Options**

A) Tree
B) Branch
C) Stack
D) Queue

**Correct Answer**

Stack

**Explanation**

The Stack data structure is used to convert infix expression to postfix expression. The purpose of stack is to reverse the order of the operators in the expression. It also serves as a storage structure, as no operator can be printed until both of its operands have appeared.

**Difficulty (0.0 – 1.0)**

0.35

**Type**

logic

**Estimated Time (seconds)**

50

---

## Question ID : DSA-0007
**Question**

What is the value of the postfix expression 6 3 2 4 + – *?

**Options**

A) 74
B) -18
C) 22
D) 40

**Correct Answer**

-18

**Explanation**

Postfix Expression is (6*(3-(2+4))) which results -18 as output.

**Difficulty (0.0 – 1.0)**

0.55

**Type**

logic

**Estimated Time (seconds)**

60

---

## Question ID : DSA-0008
**Question**

What data structure would you mostly likely see in non recursive implementation of a recursive algorithm?

**Options**

A) Stack
B) Linked List
C) Tree
D) Queue

**Correct Answer**

Stack

**Explanation**

In recursive algorithms, the order in which the recursive process comes back is the reverse of the order in which it goes forward during execution. The compiler uses the stack data structure to implement recursion. In the forwarding phase, the values of local variables, parameters and the return address are pushed into the stack at each recursion level. In the backing-out phase, the stacked address is popped and used to execute the rest of the code.

**Difficulty (0.0 – 1.0)**

0.35

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0009
**Question**

Which of the following statement(s) about stack data structure is/are NOT correct?

**Options**

A) Top of the Stack always contain the new node
B) Stack is the FIFO data structure
C) Null link is present in the last node at the bottom of the stack
D) Linked List are used for implementing Stacks

**Correct Answer**

Stack is the FIFO data structure

**Explanation**

Stack follows LIFO.

**Difficulty (0.0 – 1.0)**

0.2

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0010
**Question**

The data structure required for Breadth First Traversal on a graph is?

**Options**

A) Array
B) Stack
C) Tree
D) Queue

**Correct Answer**

Queue

**Explanation**

In Breadth First Search Traversal, BFS, starting vertex is first taken and adjacent vertices which are unvisited are also taken. Again, the first vertex which was added as an unvisited adjacent vertex list will be considered to add further unvisited vertices of the graph. To get the first unvisited vertex we need to follows First In First Out principle. Queue uses FIFO principle.

**Difficulty (0.0 – 1.0)**

0.3

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0011
**Question**

The prefix form of A-B/ (C * D ^ E) is?

**Options**

A) -A/B*C^DE
B) -A/BC*^DE
C) -ABCD*^DE
D) -/*^ACBDE

**Correct Answer**

-A/B*C^DE

**Explanation**

Infix Expression is A-B/(C*D^E) This can be written as: A-(B/(C*(D^E))) Thus prefix expression is -A/B*C^DE.

**Difficulty (0.0 – 1.0)**

0.6

**Type**

logic

**Estimated Time (seconds)**

65

---

## Question ID : DSA-0012
**Question**

Which of the following points is/are not true about Linked List data structure when it is compared with an array?

**Options**

A) Random access is not allowed in a typical implementation of Linked Lists
B) Access of elements in linked list takes less time than compared to arrays
C) Arrays have better cache locality that can make them better in terms of performance
D) It is easy to insert and delete elements in Linked List

**Correct Answer**

Access of elements in linked list takes less time than compared to arrays

**Explanation**

To access an element in a linked list, we need to traverse every element until we reach the desired element. This will take more time than arrays as arrays provide random access to its elements.

**Difficulty (0.0 – 1.0)**

0.4

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0013
**Question**

Which data structure is based on the Last In First Out (LIFO) principle?

**Options**

A) Tree
B) Linked List
C) Stack
D) Queue

**Correct Answer**

Stack

**Explanation**

The data structure that follows the Last In First Out (LIFO) principle is the Stack. It operates like a stack of objects, making it suitable for specific-order management.

**Difficulty (0.0 – 1.0)**

0.15

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0014
**Question**

Which of the following application makes use of a circular linked list?

**Options**

A) Recursive function calls
B) Undo operation in a text editor
C) Implement Hash Tables
D) Allocating CPU to resources

**Correct Answer**

Allocating CPU to resources

**Explanation**

Generally, round robin fashion is employed to allocate CPU time to resources which makes use of the circular linked list data structure. Recursive function calls use stack data structure. Undo Operation in text editor uses doubly linked lists. Hash tables uses singly linked lists.

**Difficulty (0.0 – 1.0)**

0.4

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0015
**Question**

What is a bit array?

**Options**

A) Data structure that compactly stores bits
B) Data structure for representing arrays of records
C) Array in which elements are not present in continuous locations
D) An array in which most of the elements have the same value

**Correct Answer**

Data structure that compactly stores bits

**Explanation**

It compactly stores bits and exploits bit-level parallelism.

**Difficulty (0.0 – 1.0)**

0.3

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0016
**Question**

Which of the following tree data structures is not a balanced binary tree?

**Options**

A) Splay tree
B) B-tree
C) AVL tree
D) Red-black tree

**Correct Answer**

B-tree

**Explanation**

All the tree data structures given in options are balanced, but B-tree can have more than two children.

**Difficulty (0.0 – 1.0)**

0.5

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0017
**Question**

Which of the following is not the type of queue?

**Options**

A) Priority queue
B) Circular queue
C) Single ended queue
D) Ordinary queue

**Correct Answer**

Single ended queue

**Explanation**

Queue always has two ends. So, single ended queue is not the type of queue.

**Difficulty (0.0 – 1.0)**

0.35

**Type**

logic

**Estimated Time (seconds)**

50

---

## Question ID : DSA-0018
**Question**

Which of the following data structures can be used for parentheses matching?

**Options**

A) n-ary tree
B) queue
C) priority queue
D) stack

**Correct Answer**

stack

**Explanation**

For every opening brace, push it into the stack, and for every closing brace, pop it off the stack. Do not take action for any other character. In the end, if the stack is empty, then the input has balanced parentheses.

**Difficulty (0.0 – 1.0)**

0.25

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0019
**Question**

Which algorithm is used in the top tree data structure?

**Options**

A) Backtracking
B) Divide and Conquer
C) Branch
D) Greedy

**Correct Answer**

Divide and Conquer

**Explanation**

Top tree is a type of data structure which is based on unrooted dynamic binary tree and is used to solve path related problems. It allows an algorithm called divide and conquer.

**Difficulty (0.0 – 1.0)**

0.45

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0020
**Question**

What is the need for a circular queue?

**Options**

A) easier computations
B) implement LIFO principle in queues
C) effective usage of memory
D) to delete elements based on priority

**Correct Answer**

effective usage of memory

**Explanation**

In a linear queue, dequeue operation causes the starting elements of the array to be empty, and there is no way you can use that space, while in a circular queue, you can effectively use that space. Priority queue is used to delete the elements based on their priority. Higher priority elements will be deleted first whereas lower priority elements will be deleted next. Queue data structure always follows FIFO principle.

**Difficulty (0.0 – 1.0)**

0.4

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0021
**Question**

Which of the following is the most widely used external memory data structure?

**Options**

A) B-tree
B) Red-black tree
C) AVL tree
D) Both AVL tree and Red-black tree

**Correct Answer**

B-tree

**Explanation**

In external memory, the data is transferred in form of blocks. These blocks have data valued and pointers. And B-tree can hold both the data values and pointers. So B-tree is used as an external memory data structure.

**Difficulty (0.0 – 1.0)**

0.45

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0022
**Question**

Which of the following is also known as Rope data structure?

**Options**

A) Linked List
B) Array
C) String
D) Cord

**Correct Answer**

Cord

**Explanation**

Array is a linear data structure. Strings are a collection and sequence of codes, alphabets or characters. Linked List is a linear data structure having a node containing data input and the address of the next node. The cord is also known as the rope data structure.

**Difficulty (0.0 – 1.0)**

0.4

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0023
**Question**

What will be the output of the following program?

**Options**

A) yrdnuof nas
B) foundry nas
C) sanfoundry
D) san foundry

**Correct Answer**

yrdnuof nas

**Explanation**

First, the string ‘san foundry’ is pushed one by one into the stack. When it is popped, the output will be as ‘yrdnuof nas’.

**Difficulty (0.0 – 1.0)**

0.5

**Type**

program

**Estimated Time (seconds)**

65

---

## Question ID : DSA-0024
**Question**

Which of the following data structure can provide efficient searching of the elements?

**Options**

A) binary search tree
B) unordered lists
C) 2-3 tree
D) treap

**Correct Answer**

2-3 tree

**Explanation**

The average case time for lookup in a binary search tree, treap and 2-3 tree is O(log n) and in unordered lists it is O(n). But in the worst case, only the 2-3 trees perform lookup efficiently as it takes O(log n), while others take O(n).

**Difficulty (0.0 – 1.0)**

0.55

**Type**

logic

**Estimated Time (seconds)**

55

---

## Question ID : DSA-0025
**Question**

What is an AVL tree?

**Options**

A) a tree which is unbalanced and is a height balanced tree
B) a tree which is balanced and is a height balanced tree
C) a tree with atmost 3 children
D) a tree with three children

**Correct Answer**

a tree which is balanced and is a height balanced tree

**Explanation**

It is a self balancing tree with height difference atmost 1.

**Difficulty (0.0 – 1.0)**

0.35

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0026
**Question**

What is the time complexity for searching a key or integer in Van Emde Boas data structure?

**Options**

A) O (M!)
B) O (log M!)
C) O (log (log M))
D) O (M2)

**Correct Answer**

O (log (log M))

**Explanation**

In order to search a key or integer in the Van Emde Boas data structure, the operation can be performed on an associative array. Hence, the time complexity for searching a key or integer in Van Emde Boas data structure is O (log (log M)).

**Difficulty (0.0 – 1.0)**

0.65

**Type**

logic

**Estimated Time (seconds)**

55

---

## Question ID : DSA-0027
**Question**

The optimal data structure used to solve Tower of Hanoi is _________

**Options**

A) Tree
B) Heap
C) Priority queue
D) Stack

**Correct Answer**

Stack

**Explanation**

The Tower of Hanoi involves moving of disks ‘stacked’ at one peg to another peg with respect to the size constraint. It is conveniently done using stacks and priority queues. Stack approach is widely used to solve Tower of Hanoi.

**Difficulty (0.0 – 1.0)**

0.35

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0028
**Question**

What is the use of the bin data structure?

**Options**

A) to have efficient traversal
B) to have efficient region query
C) to have efficient deletion
D) to have efficient insertion

**Correct Answer**

to have efficient region query

**Explanation**

Bin data structure allows us to have efficient region queries. A frequency of bin is increased by one each time a data point falls into a bin.

**Difficulty (0.0 – 1.0)**

0.45

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0029
**Question**

Which is the most appropriate data structure for reversing a word?

**Options**

A) stack
B) queue
C) graph
D) tree

**Correct Answer**

stack

**Explanation**

Stack is the most appropriate data structure for reversing a word because stack follows LIFO principle.

**Difficulty (0.0 – 1.0)**

0.2

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0030
**Question**

What is the functionality of the following piece of code?

**Options**

A) display the list
B) reverse the list
C) reverse the list excluding top-of-the-stack-element
D) display the list excluding top-of-the-stack-element

**Correct Answer**

display the list

**Explanation**

An alias of the node ‘first’ is created which traverses through the list and displays the elements.

**Difficulty (0.0 – 1.0)**

0.5

**Type**

program

**Estimated Time (seconds)**

65

---

## Question ID : DSA-0031
**Question**

Which of the following is the simplest data structure that supports range searching?

**Options**

A) AA-trees
B) K-d trees
C) Heaps
D) binary search trees

**Correct Answer**

K-d trees

**Explanation**

K-d trees are the simplest data structure that supports range searching and also it achieves the respectable running time.

**Difficulty (0.0 – 1.0)**

0.55

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0032
**Question**

What is the advantage of a hash table as a data structure?

**Options**

A) easy to implement
B) faster access of data
C) exhibit good locality of reference
D) very efficient for less number of entries

**Correct Answer**

faster access of data

**Explanation**

Hash table is a data structure that has an advantage that it allows fast access of elements. Hash functions are used to determine the index of any input record in a hash table.

**Difficulty (0.0 – 1.0)**

0.35

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0033
**Question**

Which type of data structure is a ternary heap?

**Options**

A) Hash
B) Array
C) Priority Stack
D) Priority Queue

**Correct Answer**

Priority Queue

**Explanation**

Ternary heap is a type of data structure in the field of computer science. It is a part of the Heap data structure family. It is a priority queue type of data structure that follows all the property of heap.

**Difficulty (0.0 – 1.0)**

0.45

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0034
**Question**

What is a deque?

**Options**

A) A queue implemented with both singly and doubly linked lists
B) A queue with insert/delete defined for front side of the queue
C) A queue with insert/delete defined for both front and rear ends of the queue
D) A queue implemented with a doubly linked list

**Correct Answer**

A queue with insert/delete defined for both front and rear ends of the queue

**Explanation**

A deque or a double ended queue is a queue with insert/delete defined for both front and rear ends of the queue.

**Difficulty (0.0 – 1.0)**

0.3

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0035
**Question**

A data structure in which elements can be inserted or deleted at/from both ends but not in the middle is?

**Options**

A) Priority queue
B) Deque
C) Circular queue
D) Queue

**Correct Answer**

Deque

**Explanation**

In deque, we can insert or delete elements from both the ends. In queue, we will follow first in first out principle for insertion and deletion of elements. Element with least priority will be deleted in a priority queue.

**Difficulty (0.0 – 1.0)**

0.3

**Type**

direct

**Estimated Time (seconds)**

25

---

## Question ID : DSA-0036
**Question**

What is the output of the following Java code?

**Options**

A) 4 and 2
B) 2 and 4
C) 5 and 3
D) 3 and 5

**Correct Answer**

3 and 5

**Explanation**

Array indexing starts from 0.

**Difficulty (0.0 – 1.0)**

0.45

**Type**

program

**Estimated Time (seconds)**

60

---

## Question ID : DSA-0037
**Question**

In simple chaining, what data structure is appropriate?

**Options**

A) Doubly linked list
B) Circular linked list
C) Singly linked list
D) Binary trees

**Correct Answer**

Doubly linked list

**Explanation**

Deletion becomes easier with doubly linked list, hence it is appropriate.

**Difficulty (0.0 – 1.0)**

0.5

**Type**

direct

**Estimated Time (seconds)**

25

---

