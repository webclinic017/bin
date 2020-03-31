
public class LinkedList {
	
	Node head;
	
	private class Node {
		int val;
		Node next;
		
		public Node(int val) {
			this.val = val;
		}
	}
	
	public static void main(String[] args) {
		LinkedList linkedList = new LinkedList();
		linkedList.head = linkedList.createLinkedList();
		printLL(linkedList.head);
//		linkedList.head = linkedList.reverseLL(linkedList.head);
//		printLL(linkedList.head);
//		linkedList.head = linkedList.reverseLLRecursive(linkedList.head);
//		printLL(linkedList.head);
//		linkedList.head = linkedList.groupReverseLL(linkedList.head, 3);
//		printLL(linkedList.head);
	}

	private static void printLL(Node node) {
		while (node != null) {
			System.out.print(node.val + " ");
			node = node.next;
		}
		System.out.println();
	}
	
	private Node createLinkedList() {
		Node node = new Node(1);
		node.next = new Node(2);
		node.next.next = new Node(3);
		node.next.next.next = new Node(4);
		node.next.next.next.next = new Node(5);
		node.next.next.next.next.next = new Node(6);
		node.next.next.next.next.next.next = new Node(7);
		node.next.next.next.next.next.next.next = new Node(8);
		node.next.next.next.next.next.next.next.next = new Node(9);
		node.next.next.next.next.next.next.next.next.next = new Node(10);
		return node;
	}
	
}
