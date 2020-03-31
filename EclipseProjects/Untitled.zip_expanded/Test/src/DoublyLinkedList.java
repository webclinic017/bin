
public class DoublyLinkedList {
	
	Node head, tail;
	
	private class Node {
		int val;
		Node next, prev;
		
		public Node(int val) {
			this.val = val;
		}
	}
	
	public static void main(String[] args) {
		DoublyLinkedList linkedList = new DoublyLinkedList();
		linkedList.createLinkedList();
		printDLLForward(linkedList.head);
		printDLLBackward(linkedList.tail);
//		linkedList.reverseDLL();
//		printDLLForward(linkedList.head);
//		printDLLBackward(linkedList.tail);
//		linkedList.reverseDLLRecursive();
//		printDLLForward(linkedList.head);
//		printDLLBackward(linkedList.tail);
//		linkedList.groupReverseDLL(3);
//		printDLLForward(linkedList.head);
//		printDLLBackward(linkedList.tail);
	}

	private static void printDLLForward(Node node) {
		System.out.print("Forward : ");
		while (node != null) {
			System.out.print(node.val + " ");
			node = node.next;
		}
		System.out.println();
	}
	
	private static void printDLLBackward(Node node) {
		System.out.print("Backward : ");
		while (node != null) {
			System.out.print(node.val + " ");
			node = node.prev;
		}
		System.out.println();
	}
	
	private Node createLinkedList() {
		push(10);
		push(9);
		push(8);
		push(7);
		push(6);
		push(5);
		push(4);
		push(3);
		push(2);
		push(1);
		return head;
	}

	private void push(int n) {
		if (head == null) {
			Node node = new Node(n);
			head = tail = node;
		} else {
			Node node = new Node(n);
			node.next = head;
			head.prev = node;
			head = node;
		}
	}
	
}
