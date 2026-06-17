import json
from pathlib import Path
from collections import Counter

trace_path = Path(r"C:\Users\admin\Downloads\Trace-20260617T110148.json")

def analyze_trace():
    print(f"Reading and parsing trace file ({trace_path.stat().st_size / 1024 / 1024:.2f} MB)...")
    
    with open(trace_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    events = data.get("traceEvents", [])
    print(f"Loaded {len(events)} trace events.")
    
    # Categories of interest
    total_tasks = 0
    long_tasks = [] # tasks > 50ms (taking 4x throttling into account, standard threshold is 50ms)
    event_names = Counter()
    categories = Counter()
    
    # Profiling sums (dur is in microseconds in Chrome Tracing)
    script_time = 0
    layout_time = 0
    recalc_style_time = 0
    paint_time = 0
    raster_time = 0
    gc_time = 0
    
    dropped_frames = 0
    presented_frames = 0
    
    # Timing markers
    markers = {}

    for ev in events:
        name = ev.get("name")
        cat = ev.get("cat", "")
        ph = ev.get("ph")
        dur = ev.get("dur", 0) # in microseconds
        ts = ev.get("ts", 0)
        
        event_names[name] += 1
        if cat:
            categories[cat] += 1
            
        # Accumulate category durations (only X phase / complete events have duration)
        if ph == "X":
            if "v8" in cat or name in ["EvaluateScript", "FunctionCall", "v8.compile", "V8.Execute"]:
                script_time += dur
            elif name == "Layout":
                layout_time += dur
            elif name == "RecalculateStyles" or name == "UpdateLayoutTree":
                recalc_style_time += dur
            elif name == "Paint":
                paint_time += dur
            elif name == "Rasterize" or name == "RasterTask":
                raster_time += dur
            elif "gc" in cat or name in ["GCEvent", "MajorGC", "MinorGC", "V8.GCEvent"]:
                gc_time += dur
                
            # Track long tasks (> 50ms = 50,000 microseconds)
            if name == "RunTask" and dur > 50000:
                long_tasks.append((dur / 1000.0, ts))
                total_tasks += 1
                
        # Track frame events
        if name == "DroppedFrame":
            dropped_frames += 1
        elif name == "DrawFrame" or name == "BeginFrame":
            presented_frames += 1
            
        # Extract markers
        if name in ["firstContentfulPaint", "largestContentfulPaint", "domContentLoadedEventEnd", "loadEventEnd"]:
            markers[name] = ts

    # Print summary
    print("\n==================================================")
    print("    CHROME TRACE ANALYSIS - DIAGNOSTIC SUMMARY    ")
    print("==================================================")
    
    print("\n--- TIMING MARKERS ---")
    if "firstContentfulPaint" in markers:
        # Convert to relative time if we can find navigation start
        print(f"First Contentful Paint (ts)   : {markers['firstContentfulPaint']}")
    if "largestContentfulPaint" in markers:
        print(f"Largest Contentful Paint (ts) : {markers['largestContentfulPaint']}")
        
    print("\n--- CPU EXPENDITURE BY CATEGORY (Microseconds to Milliseconds) ---")
    print(f"Scripting & JS Execution     : {script_time / 1000.0:.2f} ms")
    print(f"Style Recalculation          : {recalc_style_time / 1000.0:.2f} ms")
    print(f"Layout & Reflow              : {layout_time / 1000.0:.2f} ms")
    print(f"Paint & Draw                 : {paint_time / 1000.0:.2f} ms")
    print(f"Rasterization Tasks          : {raster_time / 1000.0:.2f} ms")
    print(f"Garbage Collection (V8 GC)   : {gc_time / 1000.0:.2f} ms")
    
    print("\n--- RENDERING STABILITY (JANK AUDIT) ---")
    print(f"Total Dropped Frames         : {dropped_frames}")
    print(f"Total Frame Cycles (Begin)   : {presented_frames}")
    if presented_frames > 0:
        jank_rate = (dropped_frames / (presented_frames + dropped_frames)) * 100
        print(f"Frame Drop (Jank) Rate       : {jank_rate:.2f}%")
        
    print("\n--- LONG CPU TASKS (> 50ms under 4x CPU Throttling) ---")
    print(f"Total Long Tasks Detected    : {len(long_tasks)}")
    long_tasks.sort(reverse=True, key=lambda x: x[0])
    for idx, (dur_ms, ts) in enumerate(long_tasks[:5]):
        print(f"  {idx+1}. Duration: {dur_ms:.1f} ms at timestamp {ts}")
        
    print("\n--- TOP TRACE EVENTS BY FREQUENCY ---")
    for name, count in event_names.most_common(5):
        print(f"  - {name}: {count} occurrences")
    print("==================================================\n")

if __name__ == "__main__":
    analyze_trace()
