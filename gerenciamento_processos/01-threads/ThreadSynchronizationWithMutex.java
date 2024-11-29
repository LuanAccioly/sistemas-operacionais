package threads_mutex;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Random;

public class ThreadSynchronizationWithMutex {
    private static int buffer1 = 0;
    private static int buffer2 = 0;

    private static final Lock lock1 = new ReentrantLock();
    private static final Lock lock2 = new ReentrantLock();

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
                lock1.lock();
                try {
                    System.out.println("Thread " + threadId + " acessando Buffer 1.");
                    buffer1++;
                    Thread.sleep(3000); 
                    System.out.println("Thread " + threadId + " liberando Buffer 1. Valor atual: " + buffer1);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    lock1.unlock();
                }
            } else {
                lock2.lock(); 
                try {
                    System.out.println("Thread " + threadId + " acessando Buffer 2.");
                    buffer2++;
                    Thread.sleep(3000);
                    System.out.println("Thread " + threadId + " liberando Buffer 2. Valor atual: " + buffer2);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    lock2.unlock();
                }
            }
        }
    }
}
