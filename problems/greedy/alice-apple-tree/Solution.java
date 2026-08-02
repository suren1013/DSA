public class Main {
	public static void main(String[] args) {
		int M=20;
		int K=10;
		int N=3;
		int S=2;
		int E=4;
		int W=4;
		int guaranteedSouth = S * K;
		int guaranteedMixed = E + W;
		if (M <= guaranteedSouth) {
			System.out.println(M);
		} 
		else if (M <= guaranteedSouth+guaranteedMixed) {    
		 System.out.println(M);
		 } 
		 else {
		  System.out.println(M);!
		 }
	}
}