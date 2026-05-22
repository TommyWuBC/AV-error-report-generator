from collections import Counter
from log_parser import parse_line, parse_interval_marker, classify_unparsed_line
from rules import classify_fault_event, SEVERITY_PRIORITY

def analyze_log_file(log_path):
    #counters
    #this handles number of occurence of each severity type in parsed lines
    severity_counts = Counter()
    #this is for handling unparsed lines logic
    unparsed_type_counts = Counter()
    #this is for handling timer logic
    first_timestamp = None
    last_timestamp = None
    
    with open(log_path, "r", encoding="utf-8", errors="ignore") as file:
        parsed_count = 0
        unparsed_count = 0
        unparsed_examples = []
        unparsed_examples_by_type = {}
        event_groups = {}

        for line in file:
            parsed = parse_line(line)

            if parsed is None:
                category = classify_unparsed_line(line)
                unparsed_count += 1
                unparsed_type_counts[category] += 1
                if category not in unparsed_examples_by_type:
                    unparsed_examples_by_type[category] = []

                if len(unparsed_examples_by_type[category]) < 5:
                    cleaned_line = line.strip()
                    if cleaned_line:
                        unparsed_examples_by_type[category].append(cleaned_line)
                        
                continue
            
            severity_counts[parsed["severity"]] += 1
            
            #this is for handling event groups logic of parsed lines
            if parsed["severity"] in ("WARN", "ERR", "FATAL"):
                base_message, marker = parse_interval_marker(parsed["message"])
                #create a tuple and make it the key
                key = (parsed["module"], base_message)
                if key not in event_groups:
                    #create new key value pair entry in dictionary
                    event_groups[key] = {
                        "module": parsed["module"],
                        "message": base_message,
                        "severity": parsed["severity"],
                        "count": 0,
                        "begin_count": 0,
                        "end_count": 0,
                        "first_seen": parsed["timestamp"],
                        "last_seen": parsed["timestamp"],
                    }
                event_groups[key]["count"] += 1
                event_groups[key]["last_seen"] = parsed["timestamp"]
                if marker == "begin":
                    event_groups[key]["begin_count"] += 1
                elif marker == "end":
                    event_groups[key]["end_count"] += 1
                
            parsed_count += 1
            if first_timestamp is None:
                first_timestamp = parsed["timestamp"]
            last_timestamp = parsed["timestamp"]
    
    sorted_events = sorted(
        #the dict is called event_groups, dict of <tuple, inner dict>
        event_groups.values(), #only return the values
        #this tells sorted() what to sort by, which is the count field of inner dict
        key=lambda event: (
            SEVERITY_PRIORITY.get(event["severity"], 0),
            event["count"]
        ),
        reverse=True #largest first
    )
    
    #attach diagnosis information into each event object
    for event in sorted_events[:10]:
        diagnosis = classify_fault_event(event)
        event["diagnosis"] = diagnosis
    
    #create entry (dict) of the results
    analysis_result = {
        "parsed_lines": parsed_count,
        "unparsed_lines": unparsed_count,
        "severity_counts": dict(severity_counts),
        "unparsed_categories": dict(unparsed_type_counts),
        "time_range": {
            "start": first_timestamp,
            "end": last_timestamp,
        },
        "top_fault_events": sorted_events[:10],
    }     
    return analysis_result