Before any optimization for youtube url: https://www.youtube.com/watch?v=SJKr7BPOXY0

2025-10-06 14:13:58 [INFO] services.pipeline: Total Segments: 29
2025-10-06 14:13:58 [INFO] services.pipeline: 
2025-10-06 14:13:58 [INFO] services.pipeline: ⏱️  PERFORMANCE SUMMARY:
2025-10-06 14:13:58 [INFO] services.pipeline: ────────────────────────────────────────────────────────────────────────────────
2025-10-06 14:13:58 [INFO] services.pipeline:    Download:              10.46s
2025-10-06 14:13:58 [INFO] services.pipeline:    Audio Extraction:       0.09s
2025-10-06 14:13:58 [INFO] services.pipeline:    Audio Separation:      14.16s
2025-10-06 14:13:58 [INFO] services.pipeline:    Transcription:          6.58s
2025-10-06 14:13:58 [INFO] services.pipeline:    Speaker Extraction:     1.74s
2025-10-06 14:13:58 [INFO] services.pipeline:    Voice Cloning:          6.01s
2025-10-06 14:13:58 [INFO] services.pipeline:    Translation:           79.36s
2025-10-06 14:13:58 [INFO] services.pipeline:    Synthesis:             41.29s
2025-10-06 14:13:58 [INFO] services.pipeline:    Alignment:              2.95s
2025-10-06 14:13:58 [INFO] services.pipeline:    Mixing:                 0.54s
2025-10-06 14:13:58 [INFO] services.pipeline:    Video Merge:            0.46s
2025-10-06 14:13:58 [INFO] services.pipeline: ────────────────────────────────────────────────────────────────────────────────
2025-10-06 14:13:58 [INFO] services.pipeline:    🏁 TOTAL TIME:        163.64s (2.73 minutes)
2025-10-06 14:13:58 [INFO] services.pipeline: ================================================================================


After Parallel synthesis Implementation optimization for youtube url: https://www.youtube.com/watch?v=SJKr7BPOXY0

2025-10-06 14:23:19 [INFO] services.pipeline: Output File: outputs/82a8c4cc-3036-4397-a912-785e130dbcbb_dubbed.mp4
2025-10-06 14:23:19 [INFO] services.pipeline: Total Segments: 28
2025-10-06 14:23:19 [INFO] services.pipeline: 
2025-10-06 14:23:19 [INFO] services.pipeline: ⏱️  PERFORMANCE SUMMARY:
2025-10-06 14:23:19 [INFO] services.pipeline: ────────────────────────────────────────────────────────────────────────────────
2025-10-06 14:23:19 [INFO] services.pipeline:    Download:              11.02s
2025-10-06 14:23:19 [INFO] services.pipeline:    Audio Extraction:       0.09s
2025-10-06 14:23:19 [INFO] services.pipeline:    Audio Separation:      15.39s
2025-10-06 14:23:19 [INFO] services.pipeline:    Transcription:          6.91s
2025-10-06 14:23:19 [INFO] services.pipeline:    Speaker Extraction:     1.89s
2025-10-06 14:23:19 [INFO] services.pipeline:    Voice Cloning:          6.21s
2025-10-06 14:23:19 [INFO] services.pipeline:    Translation:           61.55s
2025-10-06 14:23:19 [INFO] services.pipeline:    Synthesis:             11.76s
2025-10-06 14:23:19 [INFO] services.pipeline:    Alignment:              2.76s
2025-10-06 14:23:19 [INFO] services.pipeline:    Mixing:                 0.62s
2025-10-06 14:23:19 [INFO] services.pipeline:    Video Merge:            0.45s
2025-10-06 14:23:19 [INFO] services.pipeline: ────────────────────────────────────────────────────────────────────────────────
2025-10-06 14:23:19 [INFO] services.pipeline:    🏁 TOTAL TIME:        118.65s (1.98 minutes)
2025-10-06 14:23:19 [INFO] services.pipeline: ================================================================================

The change in segment count is at deepgram level, which varies slightly accross runs.
total improvement: (163.64s - 118.65s)/163.64s * 100 = 27.52%


After Parallel translation optimization:

2025-10-06 16:47:27 [INFO] services.pipeline: Total Segments: 29
2025-10-06 16:47:27 [INFO] services.pipeline: 
2025-10-06 16:47:27 [INFO] services.pipeline: ⏱️  PERFORMANCE SUMMARY:
2025-10-06 16:47:27 [INFO] services.pipeline: ────────────────────────────────────────────────────────────────────────────────
2025-10-06 16:47:27 [INFO] services.pipeline:    Download:              11.09s
2025-10-06 16:47:27 [INFO] services.pipeline:    Audio Extraction:       0.09s
2025-10-06 16:47:27 [INFO] services.pipeline:    Audio Separation:      15.02s
2025-10-06 16:47:27 [INFO] services.pipeline:    Transcription:          6.83s
2025-10-06 16:47:27 [INFO] services.pipeline:    Speaker Extraction:     1.79s
2025-10-06 16:47:27 [INFO] services.pipeline:    Voice Cloning:          8.06s
2025-10-06 16:47:27 [INFO] services.pipeline:    Translation:           31.63s
2025-10-06 16:47:27 [INFO] services.pipeline:    Synthesis:             11.57s
2025-10-06 16:47:27 [INFO] services.pipeline:    Alignment:              2.72s
2025-10-06 16:47:27 [INFO] services.pipeline:    Mixing:                 0.57s
2025-10-06 16:47:27 [INFO] services.pipeline:    Video Merge:            0.46s
2025-10-06 16:47:27 [INFO] services.pipeline: ────────────────────────────────────────────────────────────────────────────────
2025-10-06 16:47:27 [INFO] services.pipeline:    🏁 TOTAL TIME:         89.84s (1.50 minutes)
2025-10-06 16:47:27 [INFO] services.pipeline: ================================================================================

Total time :  89.84s
Total improvement by this optimization: (118.65s - 89.84s)/118.65s * 100 = 25.12%

After parallel running translation and voice cloning, as these are independent of each other.

2025-10-06 17:11:13 [INFO] services.pipeline: Total Segments: 28
2025-10-06 17:11:13 [INFO] services.pipeline: 
2025-10-06 17:11:13 [INFO] services.pipeline: ⏱️  PERFORMANCE SUMMARY:
2025-10-06 17:11:13 [INFO] services.pipeline: ────────────────────────────────────────────────────────────────────────────────
2025-10-06 17:11:13 [INFO] services.pipeline:    Download:               9.91s
2025-10-06 17:11:13 [INFO] services.pipeline:    Audio Extraction:       0.09s
2025-10-06 17:11:13 [INFO] services.pipeline:    Audio Separation:      15.13s
2025-10-06 17:11:13 [INFO] services.pipeline:    Transcription:          9.44s
2025-10-06 17:11:13 [INFO] services.pipeline:    Speaker Extraction:     1.87s
2025-10-06 17:11:13 [INFO] services.pipeline:    Voice Cloning:          5.76s
2025-10-06 17:11:13 [INFO] services.pipeline:    Translation:           30.76s
2025-10-06 17:11:13 [INFO] services.pipeline:    Synthesis:             12.16s
2025-10-06 17:11:13 [INFO] services.pipeline:    Alignment:              2.66s
2025-10-06 17:11:13 [INFO] services.pipeline:    Mixing:                 0.60s
2025-10-06 17:11:13 [INFO] services.pipeline:    Video Merge:            0.48s
2025-10-06 17:11:13 [INFO] services.pipeline: ────────────────────────────────────────────────────────────────────────────────
2025-10-06 17:11:13 [INFO] services.pipeline:    🏁 TOTAL TIME:         81.22s (1.35 minutes)
2025-10-06 17:11:13 [INFO] services.pipeline: ================================================================================

Total time = 81.22s
Total improvement by this optimization: (89.84s - 81.22s)/89.84s * 100 = 10.26%



After caching strategy, key: youtube url + start time + end time + language:

First run (cache misses):
2025-10-06 17:32:18 [INFO] services.pipeline: Total Segments: 29
2025-10-06 17:32:18 [INFO] services.pipeline: 
2025-10-06 17:32:18 [INFO] services.pipeline: ⏱️  PERFORMANCE SUMMARY:
2025-10-06 17:32:18 [INFO] services.pipeline: ────────────────────────────────────────────────────────────────────────────────
2025-10-06 17:32:18 [INFO] services.pipeline:    Download:              10.15s
2025-10-06 17:32:18 [INFO] services.pipeline:    Audio Extraction:       0.09s
2025-10-06 17:32:18 [INFO] services.pipeline:    Audio Separation:      15.25s
2025-10-06 17:32:18 [INFO] services.pipeline:    Transcription:          9.54s
2025-10-06 17:32:18 [INFO] services.pipeline:    Speaker Extraction:     1.76s
2025-10-06 17:32:18 [INFO] services.pipeline:    Voice Cloning:          7.74s
2025-10-06 17:32:18 [INFO] services.pipeline:    Translation:           31.40s
2025-10-06 17:32:18 [INFO] services.pipeline:    Synthesis:             11.43s
2025-10-06 17:32:18 [INFO] services.pipeline:    Alignment:              2.88s
2025-10-06 17:32:18 [INFO] services.pipeline:    Mixing:                 0.58s
2025-10-06 17:32:18 [INFO] services.pipeline:    Video Merge:            0.50s
2025-10-06 17:32:18 [INFO] services.pipeline: ────────────────────────────────────────────────────────────────────────────────
2025-10-06 17:32:18 [INFO] services.pipeline:    🏁 TOTAL TIME:         81.81s (1.36 minutes)
2025-10-06 17:32:18 [INFO] services.pipeline: ================================================================================


Second Run (with cache hits):

2025-10-06 17:53:22 [INFO] services.pipeline: Total Segments: 30
2025-10-06 17:53:22 [INFO] services.pipeline: 
2025-10-06 17:53:22 [INFO] services.pipeline: ⏱️  PERFORMANCE SUMMARY:
2025-10-06 17:53:22 [INFO] services.pipeline: ────────────────────────────────────────────────────────────────────────────────
2025-10-06 17:53:22 [INFO] services.pipeline:    Download:               9.85s
2025-10-06 17:53:22 [INFO] services.pipeline:    Audio Extraction:       0.09s
2025-10-06 17:53:22 [INFO] services.pipeline:    Audio Separation:      14.89s
2025-10-06 17:53:22 [INFO] services.pipeline:    Transcription:          0.00s
2025-10-06 17:53:22 [INFO] services.pipeline:    Speaker Extraction:     1.81s
2025-10-06 17:53:22 [INFO] services.pipeline:    Voice Cloning:          0.00s
2025-10-06 17:53:22 [INFO] services.pipeline:    Translation:            0.00s
2025-10-06 17:53:22 [INFO] services.pipeline:    Synthesis:             10.44s
2025-10-06 17:53:22 [INFO] services.pipeline:    Alignment:              2.84s
2025-10-06 17:53:22 [INFO] services.pipeline:    Mixing:                 0.59s
2025-10-06 17:53:22 [INFO] services.pipeline:    Video Merge:            0.48s
2025-10-06 17:53:22 [INFO] services.pipeline: ────────────────────────────────────────────────────────────────────────────────
2025-10-06 17:53:22 [INFO] services.pipeline:    🏁 TOTAL TIME:         40.98s (0.68 minutes)
2025-10-06 17:53:22 [INFO] services.pipeline: ================================================================================

Total time = 40.98s
Total improvement by this optimization: (81.81s - 40.98s)/81.81s * 100 = 48.56%

