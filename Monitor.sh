#!/bin/bash

# Record baseline at start
base_load=$(awk '{print $1}' /proc/loadavg)
mem_total=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
mem_available=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)
base_mem_used=$(( (mem_total - mem_available) / 1024 ))

# Initialize max deltas
max_delta_load=0
max_delta_mem=0

echo "Monitoring Load Average (1min) and Memory spikes every 5 seconds..."
echo "Baseline Load: $base_load | Baseline Mem Used: ${base_mem_used} MB"
echo "-----------------------------------------------------------"

while true
do
    interval_max_load=0
    interval_max_mem=0

    # Sample every second for 5 seconds
    for i in {1..5}
    do
        # Current load and memory
        curr_load=$(awk '{print $1}' /proc/loadavg)
        mem_available=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)
        curr_mem_used=$(( (mem_total - mem_available) / 1024 ))

        # Delta relative to baseline
        delta_load=$(echo "$curr_load - $base_load" | bc)
        delta_mem=$((curr_mem_used - base_mem_used))

        # Track max for this 5s interval
        comp=$(echo "$delta_load > $interval_max_load" | bc)
        if [ "$comp" -eq 1 ]; then
            interval_max_load=$delta_load
        fi

        if [ "$delta_mem" -gt "$interval_max_mem" ]; then
            interval_max_mem=$delta_mem
        fi

        sleep 1
    done

    # Update global max deltas
    comp=$(echo "$interval_max_load > $max_delta_load" | bc)
    if [ "$comp" -eq 1 ]; then
        max_delta_load=$interval_max_load
    fi

    if [ "$interval_max_mem" -gt "$max_delta_mem" ]; then
        max_delta_mem=$interval_max_mem
    fi

    # Display results for this 5-second interval
    printf "Highest ΔLoad (1min) in last 5s: %-6s | Highest ΔMem in last 5s: %-6s MB\n" \
           "$interval_max_load" "$interval_max_mem"
    printf "Overall Max ΔLoad: %-6s | Overall Max ΔMem: %-6s MB\n" \
           "$max_delta_load" "$max_delta_mem"
    echo "-----------------------------------------------------------"
done