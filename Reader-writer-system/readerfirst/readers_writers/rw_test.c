#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

// Global counters for performance measurement
int data = 0;
int read_count = 0;  
int write_count = 0;   
int active_writer = 0;

// Performance counters
int total_reads = 0;
int total_writes = 0;

pthread_mutex_t mutex;       
pthread_cond_t read_cond;    
pthread_cond_t write_cond;  


void* reader(void* arg) {
    int id = *((int*)arg);
    while (1) {
        pthread_mutex_lock(&mutex);
        
        while (write_count > 0 || active_writer > 0) {
            pthread_cond_wait(&read_cond, &mutex);
        }
        
        read_count++;
        pthread_mutex_unlock(&mutex);

        // Count this read operation
        pthread_mutex_lock(&mutex);
        total_reads++;
        pthread_mutex_unlock(&mutex);
       
        printf("Reader %d: read data = %d\n", id, data);
        usleep(100000); 

        pthread_mutex_lock(&mutex);
        read_count--;
        
        if (read_count == 0) {
            pthread_cond_signal(&write_cond);
        }
        pthread_mutex_unlock(&mutex);

        usleep(50000);
    }
    return NULL;
}


void* writer(void* arg) {
    int id = *((int*)arg);
    while (1) {
        pthread_mutex_lock(&mutex);
        
        write_count++;
      
        while (read_count > 0 || active_writer > 0) {
            pthread_cond_wait(&write_cond, &mutex);
        }
    
        active_writer = 1;
        pthread_mutex_unlock(&mutex);

        // Count this write operation
        pthread_mutex_lock(&mutex);
        total_writes++;
        pthread_mutex_unlock(&mutex);
       
        data++;
        printf("Writer %d: wrote data = %d\n", id, data);
        usleep(150000);

        pthread_mutex_lock(&mutex);
        active_writer = 0; 
        write_count--;     
        
        if (write_count > 0) {
            pthread_cond_signal(&write_cond);
        } else {
            pthread_cond_broadcast(&read_cond);
        }
        pthread_mutex_unlock(&mutex);

        usleep(100000); 
    }
    return NULL;
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        printf("Usage: %s <num_readers> <num_writers>\n", argv[0]);
        printf("Example: %s 5 2\n", argv[0]);
        return 1;
    }
    
    int NUM_READERS = atoi(argv[1]);
    int NUM_WRITERS = atoi(argv[2]);

    pthread_t readers[NUM_READERS];
    pthread_t writers[NUM_WRITERS];
    int reader_ids[NUM_READERS];
    int writer_ids[NUM_WRITERS];

    total_reads = 0;
    total_writes = 0;
  
    if (pthread_mutex_init(&mutex, NULL) != 0) {
        perror("mutex init failed");
        exit(EXIT_FAILURE);
    }
    if (pthread_cond_init(&read_cond, NULL) != 0 || pthread_cond_init(&write_cond, NULL) != 0) {
        perror("cond init failed");
        pthread_mutex_destroy(&mutex);
        exit(EXIT_FAILURE);
    }


    for (int i = 0; i < NUM_READERS; i++) {
        reader_ids[i] = i;
        if (pthread_create(&readers[i], NULL, reader, &reader_ids[i]) != 0) {
            perror("Failed to create reader thread");
            exit(EXIT_FAILURE);
        }
    }
 
    
    for (int i = 0; i < NUM_WRITERS; i++) {
        writer_ids[i] = i;
        if (pthread_create(&writers[i], NULL, writer, &writer_ids[i]) != 0) {
            perror("Failed to create writer thread");
            exit(EXIT_FAILURE);
        }
    }
 
  
    sleep(5);
 

    for (int i = 0; i < NUM_READERS; i++) {
        pthread_cancel(readers[i]);
    }
    for (int i = 0; i < NUM_WRITERS; i++) {
        pthread_cancel(writers[i]);
    }

    for (int i = 0; i < NUM_READERS; i++) {
        pthread_join(readers[i], NULL);
    }
    for (int i = 0; i < NUM_WRITERS; i++) {
        pthread_join(writers[i], NULL);
    }

    pthread_mutex_destroy(&mutex);
    pthread_cond_destroy(&read_cond);
    pthread_cond_destroy(&write_cond);

    printf("Simulation finished. Final data = %d\n", data);
    printf("CSV_OUTPUT:%d,%d,%d,%d,%d,%d\n", NUM_READERS, NUM_WRITERS, total_reads, total_writes, data, 0);
    return 0;
}