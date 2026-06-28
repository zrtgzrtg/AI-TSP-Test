# ============================================================
# CONFIG
# ============================================================

analysis_name <- "tsp_exp"   # <-- change this name
data_dir <- "data"           # <-- folder where your JSON files are

# ============================================================
# Load packages
# ============================================================

packages <- c("jsonlite", "dplyr", "purrr", "tidyr", "stringr", "ggplot2", "tibble")

missing_packages <- packages[!sapply(packages, requireNamespace, quietly = TRUE)]

if (length(missing_packages) > 0) {
  install.packages(missing_packages)
}

library(jsonlite)
library(dplyr)
library(purrr)
library(tidyr)
library(stringr)
library(ggplot2)
library(tibble)

# ============================================================
# Helper functions
# ============================================================

safe_analysis_name <- analysis_name %>%
  str_replace_all("[^A-Za-z0-9_\\-]", "_")

to_num <- function(x) {
  if (is.null(x)) return(NA_real_)
  suppressWarnings(as.numeric(x))
}

to_bool <- function(x) {
  if (is.null(x)) return(FALSE)
  if (is.logical(x)) return(isTRUE(x))
  if (is.numeric(x)) return(!is.na(x) && x != 0)
  if (is.character(x)) return(tolower(x) %in% c("true", "t", "yes", "y", "1"))
  FALSE
}

get_value <- function(x, name, default = NULL) {
  if (!is.list(x)) return(default)
  if (is.null(x[[name]])) return(default)
  x[[name]]
}

# Main statistics function
# Only use this on already-filtered valid results.
summarise_performance <- function(.data) {
  .data %>%
    summarise(
      n = n(),
      mean_improvement_pct = mean(improvement_pct, na.rm = TRUE),
      median_improvement_pct = median(improvement_pct, na.rm = TRUE),
      sd_improvement_pct = sd(improvement_pct, na.rm = TRUE),
      min_improvement_pct = min(improvement_pct, na.rm = TRUE),
      max_improvement_pct = max(improvement_pct, na.rm = TRUE),
      win_rate_pct = mean(improvement_pct > 0, na.rm = TRUE) * 100,
      tie_rate_pct = mean(improvement_pct == 0, na.rm = TRUE) * 100,
      loss_rate_pct = mean(improvement_pct < 0, na.rm = TRUE) * 100,
      mean_ai_distance = mean(ai_distance, na.rm = TRUE),
      mean_other_distance = mean(other_distance, na.rm = TRUE),
      .groups = "drop"
    )
}

# ============================================================
# Import one JSON file
# ============================================================

read_result_json <- function(json_path) {
  
  raw_results <- fromJSON(json_path, simplifyVector = FALSE)
  
  heuristics <- c("NN", "CI", "FI", "NN2opt", "CI2opt", "FI2opt", "LKH")
  
  source_file <- basename(json_path)
  problem_name <- tools::file_path_sans_ext(source_file)
  problem_size <- as.integer(str_extract(problem_name, "\\d+"))
  
  instance_names <- names(raw_results)[
    str_detect(names(raw_results), "^size\\d+_\\d+\\.txt$")
  ]
  
  instance_names <- instance_names[
    map_lgl(instance_names, function(nm) {
      x <- raw_results[[nm]]
      is.list(x) && any(heuristics %in% names(x))
    })
  ]
  
  cat("\nReading:", json_path, "\n")
  cat("Found instance entries:", length(instance_names), "\n")
  
  results_long <- map_dfr(instance_names, function(instance_name) {
    
    instance <- raw_results[[instance_name]]
    
    map_dfr(heuristics, function(h) {
      
      x <- get_value(instance, h, default = list())
      
      tibble(
        analysis_name = analysis_name,
        source_file = source_file,
        problem_name = problem_name,
        problem_size = problem_size,
        instance = instance_name,
        instance_id = as.integer(str_extract(instance_name, "(?<=_)\\d+(?=\\.txt)")),
        size = as.integer(str_extract(instance_name, "(?<=size)\\d+")),
        heuristic = h,
        other_distance = to_num(get_value(x, "other_distance")),
        ai_distance = to_num(get_value(x, "ai_distance")),
        improvement_pct = to_num(get_value(x, "improvement_pct")),
        excluded_by_cutoff = to_bool(get_value(x, "excluded_by_cutoff")),
        excluded_by_failed = to_bool(get_value(x, "excluded_by_failed"))
      )
    })
  })
  
  instance_summary <- map_dfr(instance_names, function(instance_name) {
    
    instance <- raw_results[[instance_name]]
    
    tibble(
      analysis_name = analysis_name,
      source_file = source_file,
      problem_name = problem_name,
      problem_size = problem_size,
      instance = instance_name,
      instance_id = as.integer(str_extract(instance_name, "(?<=_)\\d+(?=\\.txt)")),
      size = as.integer(str_extract(instance_name, "(?<=size)\\d+")),
      average_improvement_pct = to_num(get_value(instance, "average_improvement_pct")),
      filtered_average_improvement_pct = to_num(get_value(instance, "filtered_average_improvement_pct")),
      num_excluded_by_cutoff_json = to_num(get_value(instance, "num_excluded_by_cutoff")),
      num_excluded_by_failed_json = to_num(get_value(instance, "num_excluded_by_failed"))
    )
  })
  
  list(
    results_long = results_long,
    instance_summary = instance_summary
  )
}

# ============================================================
# Read all JSON files
# ============================================================

json_files <- list.files(data_dir, pattern = "\\.json$", full.names = TRUE)

if (length(json_files) == 0) {
  stop("No JSON files found in: ", data_dir)
}

print(json_files)

all_results <- map(json_files, read_result_json)

results_long <- map_dfr(all_results, "results_long")
instance_summary <- map_dfr(all_results, "instance_summary")

# ============================================================
# Add validity and exclusion reason
# ============================================================

results_long <- results_long %>%
  mutate(
    invalid_numeric =
      is.na(improvement_pct) |
      is.na(ai_distance) |
      is.na(other_distance),
    
    exclusion_reason = case_when(
      excluded_by_failed ~ "failed",
      excluded_by_cutoff ~ "cutoff",
      invalid_numeric ~ "invalid_numeric",
      TRUE ~ "used"
    ),
    
    valid_for_statistics = exclusion_reason == "used"
  )

# ============================================================
# Factor ordering
# ============================================================

heuristic_order <- c("NN", "CI", "FI", "NN2opt", "CI2opt", "FI2opt", "LKH")

results_long <- results_long %>%
  mutate(
    heuristic = factor(heuristic, levels = heuristic_order),
    size = factor(size, levels = sort(unique(size))),
    exclusion_reason = factor(
      exclusion_reason,
      levels = c("used", "failed", "cutoff", "invalid_numeric")
    )
  )

instance_summary <- instance_summary %>%
  mutate(
    size = factor(size, levels = sort(unique(size)))
  )

# ============================================================
# Clean performance tables
# ============================================================

valid_results <- results_long %>%
  filter(valid_for_statistics)

performance_by_heuristic <- valid_results %>%
  group_by(analysis_name, size, heuristic) %>%
  summarise_performance() %>%
  arrange(size, heuristic)

performance_by_size <- valid_results %>%
  group_by(analysis_name, size) %>%
  summarise_performance() %>%
  arrange(size)

lkh_summary <- valid_results %>%
  filter(heuristic == "LKH") %>%
  group_by(analysis_name, size, heuristic) %>%
  summarise_performance() %>%
  arrange(size)

# Simple, non-advanced exclusion summary
exclusion_summary <- results_long %>%
  group_by(analysis_name, size) %>%
  summarise(
    n_instances = n_distinct(instance),
    total_comparisons = n(),
    used_comparisons = sum(exclusion_reason == "used"),
    failed_comparisons = sum(exclusion_reason == "failed"),
    cutoff_comparisons = sum(exclusion_reason == "cutoff"),
    invalid_numeric_comparisons = sum(exclusion_reason == "invalid_numeric"),
    not_used_comparisons = total_comparisons - used_comparisons,
    .groups = "drop"
  ) %>%
  arrange(size)

# Optional: simple exclusion summary by heuristic
exclusion_by_heuristic <- results_long %>%
  group_by(analysis_name, size, heuristic) %>%
  summarise(
    total_comparisons = n(),
    used_comparisons = sum(exclusion_reason == "used"),
    failed_comparisons = sum(exclusion_reason == "failed"),
    cutoff_comparisons = sum(exclusion_reason == "cutoff"),
    invalid_numeric_comparisons = sum(exclusion_reason == "invalid_numeric"),
    not_used_comparisons = total_comparisons - used_comparisons,
    .groups = "drop"
  ) %>%
  arrange(size, heuristic)

# ============================================================
# Output folders
# ============================================================

dir.create("tables", showWarnings = FALSE)
dir.create("plots", showWarnings = FALSE)

# ============================================================
# Save tables
# ============================================================

write.csv(
  results_long,
  paste0("tables/", safe_analysis_name, "_results_long.csv"),
  row.names = FALSE
)

write.csv(
  instance_summary,
  paste0("tables/", safe_analysis_name, "_instance_summary.csv"),
  row.names = FALSE
)

write.csv(
  performance_by_heuristic,
  paste0("tables/", safe_analysis_name, "_performance_by_heuristic.csv"),
  row.names = FALSE
)

write.csv(
  performance_by_size,
  paste0("tables/", safe_analysis_name, "_performance_by_size.csv"),
  row.names = FALSE
)

write.csv(
  lkh_summary,
  paste0("tables/", safe_analysis_name, "_lkh_summary.csv"),
  row.names = FALSE
)

write.csv(
  exclusion_summary,
  paste0("tables/", safe_analysis_name, "_exclusion_summary.csv"),
  row.names = FALSE
)

write.csv(
  exclusion_by_heuristic,
  paste0("tables/", safe_analysis_name, "_exclusion_by_heuristic.csv"),
  row.names = FALSE
)

# ============================================================
# Plots
# ============================================================

# Plot 1: Mean improvement by heuristic
p1 <- performance_by_heuristic %>%
  ggplot(aes(x = heuristic, y = mean_improvement_pct, fill = size)) +
  geom_col(position = "dodge") +
  geom_hline(yintercept = 0, linetype = "dashed") +
  labs(
    title = paste0(analysis_name, ": Mean AI improvement by heuristic"),
    subtitle = "Only valid comparisons are used",
    x = "Heuristic",
    y = "Mean improvement (%)",
    fill = "Instance size"
  ) +
  theme_minimal()

ggsave(
  paste0("plots/", safe_analysis_name, "_mean_improvement_by_heuristic.png"),
  p1,
  width = 10,
  height = 6,
  dpi = 300
)

# Plot 2: Boxplot of improvement distribution
p2 <- valid_results %>%
  ggplot(aes(x = heuristic, y = improvement_pct)) +
  geom_boxplot() +
  geom_hline(yintercept = 0, linetype = "dashed") +
  facet_wrap(~ size) +
  labs(
    title = paste0(analysis_name, ": Distribution of AI improvement"),
    subtitle = "Only valid comparisons are used",
    x = "Heuristic",
    y = "Improvement (%)"
  ) +
  theme_minimal()

ggsave(
  paste0("plots/", safe_analysis_name, "_improvement_distribution_boxplot.png"),
  p2,
  width = 10,
  height = 6,
  dpi = 300
)

# Plot 3: AI vs LKH
p3 <- lkh_summary %>%
  ggplot(aes(x = size, y = mean_improvement_pct, group = 1)) +
  geom_line() +
  geom_point(size = 3) +
  geom_hline(yintercept = 0, linetype = "dashed") +
  labs(
    title = paste0(analysis_name, ": AI performance relative to LKH"),
    subtitle = "Negative values mean AI is worse than LKH",
    x = "Instance size",
    y = "Mean improvement vs LKH (%)"
  ) +
  theme_minimal()

ggsave(
  paste0("plots/", safe_analysis_name, "_ai_vs_lkh.png"),
  p3,
  width = 8,
  height = 5,
  dpi = 300
)

# Plot 4: Simple exclusion counts
exclusion_plot_data <- exclusion_summary %>%
  select(
    size,
    failed_comparisons,
    cutoff_comparisons,
    invalid_numeric_comparisons
  ) %>%
  pivot_longer(
    cols = c(
      failed_comparisons,
      cutoff_comparisons,
      invalid_numeric_comparisons
    ),
    names_to = "reason",
    values_to = "count"
  )

p4 <- exclusion_plot_data %>%
  ggplot(aes(x = size, y = count, fill = reason)) +
  geom_col(position = "dodge") +
  labs(
    title = paste0(analysis_name, ": Excluded comparisons"),
    x = "Instance size",
    y = "Number of comparisons",
    fill = "Reason"
  ) +
  theme_minimal()

ggsave(
  paste0("plots/", safe_analysis_name, "_excluded_comparisons.png"),
  p4,
  width = 8,
  height = 5,
  dpi = 300
)

# ============================================================
# Print important summaries
# ============================================================

cat("\nDone.\n")
cat("Analysis name:", analysis_name, "\n")
cat("Data directory:", data_dir, "\n")
cat("Tables saved in: tables/\n")
cat("Plots saved in: plots/\n\n")

cat("Performance by heuristic:\n")
print(performance_by_heuristic)

cat("\nAI vs LKH summary:\n")
print(lkh_summary)

cat("\nSimple exclusion summary:\n")
print(exclusion_summary)