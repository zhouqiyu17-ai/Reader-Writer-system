#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

// Shared data
int data = 0;
int read_count = 0; // Number of active readers
int writer_active = 0; // Flag if a writer currently has exclusive access

// Synchronization variables
pthread_mutex_t mutex;
pthread_cond_t cond_var;

// Reader function
void* reader(void* arg) {
    int id = *((int*)arg);
    while (1) {
        // Wait for any active writer to finish
        pthread_mutex_lock(&mutex);
        while (writer_active) {
            pthread_cond_wait(&cond_var, &mutex);
        }
        read_count++;
        pthread_mutex_unlock(&mutex);

        // Simulate reading
        printf("Reader %d: read data = %d\n", id, data);
        // Simulate reading time
        usleep(100000); // 100ms

        // Exit critical section for updating read_count
        pthread_mutex_lock(&mutex);
        read_count--;
        if (read_count == 0) {
            // Wake writers when no readers remain
            pthread_cond_signal(&cond_var);
        }
        pthread_mutex_unlock(&mutex);

        // Simulate some delay before next read
        usleep(50000); // 50ms
    }
    return NULL;
}

// Writer function
void* writer(void* arg) {
    int id = *((int*)arg);
    while (1) {
        pthread_mutex_lock(&mutex);
        while (writer_active || read_count > 0) {
            pthread_cond_wait(&cond_var, &mutex);
        }
        writer_active = 1;
        pthread_mutex_unlock(&mutex);

        // Simulate writing
        data++;
        printf("Writer %d: wrote data = %d\n", id, data);
        // Simulate writing time
        usleep(150000); // 150ms

        pthread_mutex_lock(&mutex);
        writer_active = 0;
        pthread_cond_broadcast(&cond_var);
        pthread_mutex_unlock(&mutex);

        // Simulate some delay before next write
        usleep(100000); // 100ms
    }
    return NULL;
}

int main() {
    const int NUM_READERS = 5;
    const int NUM_WRITERS = 3;

    pthread_t readers[NUM_READERS];
    pthread_t writers[NUM_WRITERS];
    int reader_ids[NUM_READERS];
    int writer_ids[NUM_WRITERS];

    // Initialize synchronization variables
    pthread_mutex_init(&mutex, NULL);
    pthread_cond_init(&cond_var, NULL);

    // Create reader threads
    for (int i = 0; i < NUM_READERS; i++) {
        reader_ids[i] = i;
        if (pthread_create(&readers[i], NULL, reader, &reader_ids[i]) != 0) {
            perror("Failed to create reader thread");
            exit(EXIT_FAILURE);
        }
    }

    // Create writer threads
    for (int i = 0; i < NUM_WRITERS; i++) {
        writer_ids[i] = i;
        if (pthread_create(&writers[i], NULL, writer, &writer_ids[i]) != 0) {
            perror("Failed to create writer thread");
            exit(EXIT_FAILURE);
        }
    }

    // Wait for threads to finish (they run infinitely, so we'll wait for a while then exit)
    // In a real scenario, we would have a condition to stop after some time or iterations.
    // For simplicity, we'll let them run for a fixed time and then cancel.
    sleep(5); // Let the simulation run for 5 seconds

    // Cancel threads (since they are in infinite loops)
    for (int i = 0; i < NUM_READERS; i++) {
        pthread_cancel(readers[i]);
    }
    for (int i = 0; i < NUM_WRITERS; i++) {
        pthread_cancel(writers[i]);
    }

    // Join threads
    for (int i = 0; i < NUM_READERS; i++) {
        pthread_join(readers[i], NULL);
    }
    for (int i = 0; i < NUM_WRITERS; i++) {
        pthread_join(writers[i], NULL);
    }

    // Cleanup
    pthread_mutex_destroy(&mutex);
    pthread_cond_destroy(&cond_var);

    printf("Simulation finished.\n");
    return 0;
}