package threads_mutex;
import java.util.Random;

public class ThreadSynchronizationNoMutex {
    private static int buffer1 = 0;
    private static int buffer2 = 0;

    public static void main(String[] args) {
        for (int i = 1; i <= 5; i++) {
            Thread thread = new Thread(new Task(i));
            thread.start();
        }
    }

    static class Task implements Runnable {
        private final int threadId;
        private final Random random = new Random();

        public Task(int threadId) {
            this.threadId = threadId;
        }

        @Override
        public void run() {
            while (true) {
                int bufferChoice = random.nextInt(2) + 1; 
                accessBuffer(bufferChoice);

                try {
                    Thread.sleep(random.nextInt(2000) + 1000); 
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    System.err.println("Thread " + threadId + " foi interrompida.");
                }
            }
        }

        private void accessBuffer(int bufferChoice) {
            if (bufferChoice == 1) {
                System.out.println("Thread " + threadId + " acessando Buffer 1.");
                buffer1++;
                try {
                    Thread.sleep(3000); 
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                System.out.println("Thread " + threadId + " liberando Buffer 1. Valor atual: " + buffer1);
            } else {
                System.out.println("Thread " + threadId + " acessando Buffer 2.");
                buffer2++;
                try {
                    Thread.sleep(3000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                System.out.println("Thread " + threadId + " liberando Buffer 2. Valor atual: " + buffer2);
            }
        }
    }
}
