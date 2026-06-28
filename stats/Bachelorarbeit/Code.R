library(jsonlite)
library(dplyr)
library(purrr)
library(stringr)
library(tibble)
library(tidyr)
library(ggplot2)

# ------------------------------------------------------------
# 1. Load all JSON files
# ------------------------------------------------------------

folder <- "./FinalResults"

json_files <- list.files(
  path = folder,
  pattern = "^results[0-9]+\\.json$",
  full.names = TRUE
)

json_files <- json_files[
  order(as.numeric(str_extract(basename(json_files), "\\d+")))
]

results_list <- map(json_files, ~ fromJSON(.x, simplifyVector = FALSE))

names(results_list) <- tools::file_path_sans_ext(basename(json_files))


# ------------------------------------------------------------
# 2. Helper functions
# ------------------------------------------------------------

heuristic_order <- c(
  "NN",
  "CI",
  "FI",
  "NN2opt",
  "CI2opt",
  "FI2opt",
  "LKH"
)

heuristic_cols <- c(
  "NN" = "#1B9E77",
  "CI" = "#D95F02",
  "FI" = "#7570B3",
  "NN2opt" = "#E7298A",
  "CI2opt" = "#66A61E",
  "FI2opt" = "#E6AB02",
  "LKH" = "#666666"
)

safe_num <- function(x) {
  if (is.null(x) || length(x) == 0) {
    return(NA_real_)
  }
  
  x <- x[[1]]
  out <- suppressWarnings(as.numeric(x))
  
  if (length(out) == 0 || is.na(out)) {
    return(NA_real_)
  }
  
  out
}

safe_bool <- function(x) {
  if (is.null(x) || length(x) == 0) {
    return(FALSE)
  }
  
  isTRUE(as.logical(x[[1]]))
}

is_heuristic_entry <- function(x) {
  is.list(x) &&
    all(c(
      "other_distance",
      "ai_distance",
      "improvement_pct",
      "excluded_by_cutoff",
      "excluded_by_failed"
    ) %in% names(x))
}

mean_na <- function(x) {
  if (all(is.na(x))) {
    NA_real_
  } else {
    mean(x, na.rm = TRUE)
  }
}


# ------------------------------------------------------------
# 3. Create one big clean table
# ------------------------------------------------------------

big_table <- imap_dfr(results_list, function(json_data, result_name) {
  
  # Remove the last 3 top-level JSON objects.
  json_data <- json_data[seq_len(length(json_data) - 3)]
  
  run_names <- names(json_data)[
    str_detect(names(json_data), "^size\\d+_\\d+(\\.txt)?$")
  ]
  
  map_dfr(run_names, function(run_name) {
    
    run_data <- json_data[[run_name]]
    
    size <- as.integer(str_match(run_name, "^size(\\d+)_")[, 2])
    run_id <- as.integer(str_match(run_name, "_(\\d+)(\\.txt)?$")[, 2])
    
    heuristic_names <- names(run_data)[
      map_lgl(run_data, is_heuristic_entry)
    ]
    
    heuristic_names <- c(
      intersect(heuristic_order, heuristic_names),
      setdiff(heuristic_names, heuristic_order)
    )
    
    map_dfr(heuristic_names, function(heuristic_name) {
      
      entry <- run_data[[heuristic_name]]
      
      excluded_by_cutoff <- safe_bool(entry$excluded_by_cutoff)
      excluded_by_failed <- safe_bool(entry$excluded_by_failed)
      
      excluded <- excluded_by_cutoff | excluded_by_failed
      
      other_distance_value <- safe_num(entry$other_distance)
      ai_distance_value <- safe_num(entry$ai_distance)
      improvement_pct_value <- safe_num(entry$improvement_pct)
      
      tibble(
        size = size,
        run_id = run_id,
        heuristic = heuristic_name,
        
        other_distance = if (excluded) NA_real_ else other_distance_value,
        ai_distance = if (excluded) NA_real_ else ai_distance_value,
        improvement_pct = if (excluded) NA_real_ else improvement_pct_value,
        
        excluded_by_cutoff = excluded_by_cutoff,
        excluded_by_failed = excluded_by_failed
      )
    })
  })
}) %>%
  mutate(
    heuristic = factor(heuristic, levels = heuristic_order)
  ) %>%
  arrange(size, run_id, heuristic)


# ------------------------------------------------------------
# 4. Mean table by size and heuristic
# ------------------------------------------------------------

mean_table <- big_table %>%
  group_by(size, heuristic) %>%
  summarise(
    n_total = n(),
    n_used = sum(!is.na(improvement_pct)),
    
    mean_other_distance = mean_na(other_distance),
    mean_ai_distance = mean_na(ai_distance),
    mean_improvement_pct = mean_na(improvement_pct),
    
    .groups = "drop"
  ) %>%
  arrange(size, heuristic)

View(mean_table)


# ------------------------------------------------------------
# 5. Shared plot theme and plotting table
# ------------------------------------------------------------

theme_ai <- theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold"),
    plot.subtitle = element_text(size = 11),
    legend.position = "bottom",
    panel.grid.minor = element_blank(),
    strip.text = element_text(face = "bold"),
    axis.text.x = element_text(angle = 30, hjust = 1)
  )

plot_table <- big_table %>%
  mutate(
    distance_diff = other_distance - ai_distance,
    
    outcome = case_when(
      is.na(improvement_pct) ~ NA_character_,
      improvement_pct > 0 ~ "AI better",
      improvement_pct < 0 ~ "AI worse",
      TRUE ~ "Tie"
    ),
    
    outcome = factor(
      outcome,
      levels = c("AI better", "Tie", "AI worse")
    )
  )


# ------------------------------------------------------------
# 6. Boxplot: AI improvement distribution
# ------------------------------------------------------------
# Positive = AI better
# Negative = AI worse
# Dashed line at 0 = equal performance
# White diamond = mean

plot_boxplot_improvement <- ggplot(
  big_table,
  aes(x = heuristic, y = improvement_pct, fill = heuristic)
) +
  geom_hline(
    yintercept = 0,
    linetype = "dashed",
    linewidth = 0.7,
    color = "grey35"
  ) +
  geom_boxplot(
    na.rm = TRUE,
    alpha = 0.75,
    outlier.alpha = 0.45
  ) +
  stat_summary(
    fun = mean,
    geom = "point",
    shape = 23,
    size = 2.5,
    fill = "white",
    color = "black",
    na.rm = TRUE
  ) +
  facet_wrap(~ size, scales = "free_y") +
  scale_fill_manual(values = heuristic_cols) +
  labs(
    title = "Distribution of AI Improvement over Heuristics",
    subtitle = "Boxplots show variation across runs; white diamonds show the mean",
    x = "Heuristic",
    y = "AI improvement over heuristic (%)",
    fill = "Heuristic"
  ) +
  theme_ai

plot_boxplot_improvement


# ------------------------------------------------------------
# 7. Lineplot: mean improvement over problem size
# ------------------------------------------------------------
# Shows how AI performance changes as size grows.

plot_line_mean_improvement <- ggplot(
  mean_table,
  aes(
    x = size,
    y = mean_improvement_pct,
    color = heuristic,
    group = heuristic
  )
) +
  geom_hline(
    yintercept = 0,
    linetype = "dashed",
    linewidth = 0.7,
    color = "grey35"
  ) +
  geom_line(linewidth = 1) +
  geom_point(size = 2.5) +
  scale_color_manual(values = heuristic_cols) +
  labs(
    title = "Mean AI Improvement by Problem Size",
    subtitle = "Positive values indicate that AI is better than the heuristic on average",
    x = "Problem size",
    y = "Mean AI improvement over heuristic (%)",
    color = "Heuristic"
  ) +
  theme_ai +
  theme(axis.text.x = element_text(angle = 0))

plot_line_mean_improvement


# ------------------------------------------------------------
# 8. Heatmap: mean improvement by size and heuristic
# ------------------------------------------------------------
# Blue = AI better
# Red = AI worse
# White = approximately equal

plot_heatmap_improvement <- ggplot(
  mean_table,
  aes(
    x = heuristic,
    y = factor(size),
    fill = mean_improvement_pct
  )
) +
  geom_tile(color = "white", linewidth = 0.4) +
  geom_text(
    aes(label = ifelse(is.na(mean_improvement_pct), "", round(mean_improvement_pct, 1))),
    size = 3
  ) +
  scale_fill_gradient2(
    low = "#B2182B",
    mid = "white",
    high = "#2166AC",
    midpoint = 0,
    na.value = "grey85"
  ) +
  labs(
    title = "Mean AI Improvement Heatmap",
    subtitle = "Blue = AI better, red = AI worse, white = approximately equal",
    x = "Heuristic",
    y = "Problem size",
    fill = "Mean improvement (%)"
  ) +
  theme_ai

plot_heatmap_improvement


# ------------------------------------------------------------
# 9. Scatterplot: AI distance vs heuristic distance
# ------------------------------------------------------------
# Points below the dashed equality line mean:
# AI distance < heuristic distance, so AI is better.

plot_scatter_distance <- ggplot(
  plot_table,
  aes(
    x = other_distance,
    y = ai_distance,
    color = heuristic
  )
) +
  geom_abline(
    slope = 1,
    intercept = 0,
    linetype = "dashed",
    linewidth = 0.7,
    color = "grey35"
  ) +
  geom_point(
    alpha = 0.65,
    size = 2,
    na.rm = TRUE
  ) +
  facet_wrap(~ size, scales = "free") +
  scale_color_manual(values = heuristic_cols) +
  labs(
    title = "AI Distance vs Heuristic Distance",
    subtitle = "Points below the dashed line indicate that AI found a shorter route",
    x = "Heuristic distance",
    y = "AI distance",
    color = "Heuristic"
  ) +
  theme_ai +
  theme(axis.text.x = element_text(angle = 0))

plot_scatter_distance


# ------------------------------------------------------------
# 10. Difference plot: absolute distance advantage
# ------------------------------------------------------------
# distance_diff = other_distance - ai_distance
#
# Positive values: AI is better
# Negative values: heuristic is better

plot_difference_distance <- ggplot(
  plot_table,
  aes(
    x = heuristic,
    y = distance_diff,
    fill = heuristic
  )
) +
  geom_hline(
    yintercept = 0,
    linetype = "dashed",
    linewidth = 0.7,
    color = "grey35"
  ) +
  geom_boxplot(
    alpha = 0.75,
    outlier.alpha = 0.4,
    na.rm = TRUE
  ) +
  stat_summary(
    fun = mean,
    geom = "point",
    shape = 23,
    size = 2.5,
    fill = "white",
    color = "black",
    na.rm = TRUE
  ) +
  facet_wrap(~ size, scales = "free_y") +
  scale_fill_manual(values = heuristic_cols) +
  labs(
    title = "Absolute Distance Difference: AI vs Heuristic",
    subtitle = "Positive values mean AI found a shorter route; white diamonds show the mean",
    x = "Heuristic",
    y = "Heuristic distance - AI distance",
    fill = "Heuristic"
  ) +
  theme_ai

plot_difference_distance


# ------------------------------------------------------------
# 11. Win / tie / loss plot
# ------------------------------------------------------------
# AI better: improvement_pct > 0
# Tie: improvement_pct == 0
# AI worse: improvement_pct < 0

win_loss_table <- plot_table %>%
  filter(!is.na(outcome)) %>%
  count(size, heuristic, outcome, name = "n") %>%
  group_by(size, heuristic) %>%
  mutate(
    pct = n / sum(n)
  ) %>%
  ungroup()

plot_win_loss <- ggplot(
  win_loss_table,
  aes(
    x = heuristic,
    y = pct,
    fill = outcome
  )
) +
  geom_col(
    width = 0.75,
    color = "white",
    linewidth = 0.25
  ) +
  facet_wrap(~ size) +
  scale_y_continuous(
    labels = function(x) paste0(round(100 * x), "%")
  ) +
  scale_fill_manual(
    values = c(
      "AI better" = "#2166AC",
      "Tie" = "grey75",
      "AI worse" = "#B2182B"
    )
  ) +
  labs(
    title = "AI Win / Tie / Loss Rate by Heuristic",
    subtitle = "Based on improvement percentage for each valid run",
    x = "Heuristic",
    y = "Share of valid runs",
    fill = "Outcome"
  ) +
  theme_ai

plot_win_loss


# ------------------------------------------------------------
# 12. Failure and cutoff rate plot
# ------------------------------------------------------------
# Each size-run is counted only once.
# Otherwise, one failed AI run would be counted once for every heuristic.

failure_rate_table <- big_table %>%
  group_by(size, run_id) %>%
  summarise(
    failed = any(excluded_by_failed, na.rm = TRUE),
    cutoff = any(excluded_by_cutoff, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  group_by(size) %>%
  summarise(
    n_runs = n(),
    failed_runs = sum(failed),
    cutoff_runs = sum(cutoff),
    
    failure_rate = 100 * failed_runs / n_runs,
    cutoff_rate = 100 * cutoff_runs / n_runs,
    
    .groups = "drop"
  )

exclusion_rate_long <- failure_rate_table %>%
  select(size, failure_rate, cutoff_rate) %>%
  pivot_longer(
    cols = c(failure_rate, cutoff_rate),
    names_to = "type",
    values_to = "rate"
  ) %>%
  mutate(
    type = recode(
      type,
      failure_rate = "Failed",
      cutoff_rate = "Cutoff"
    )
  )

plot_failure_rate <- ggplot(
  exclusion_rate_long,
  aes(
    x = size,
    y = rate,
    color = type,
    group = type
  )
) +
  geom_hline(
    yintercept = 0,
    linetype = "dashed",
    linewidth = 0.7,
    color = "grey35"
  ) +
  geom_line(linewidth = 1) +
  geom_point(size = 2.6) +
  scale_y_continuous(
    labels = function(x) paste0(x, "%")
  ) +
  scale_color_manual(
    values = c(
      "Failed" = "#B2182B",
      "Cutoff" = "#E69F00"
    )
  ) +
  labs(
    title = "Failure and Cutoff Rate by Problem Size",
    subtitle = "Each run is counted once, not once per heuristic",
    x = "Problem size",
    y = "Rate",
    color = "Exclusion reason"
  ) +
  theme_ai +
  theme(axis.text.x = element_text(angle = 0))

plot_failure_rate

# ------------------------------------------------------------
# Overall mean improvement percentage over all valid runs
# ------------------------------------------------------------
# Positive values mean AI is better than the heuristic.
# Negative values mean AI is worse than the heuristic.
# AI itself is added as a 0% baseline.

overall_improvement_table <- big_table %>%
  group_by(heuristic) %>%
  summarise(
    n_used = sum(!is.na(improvement_pct)),
    mean_improvement_pct = mean(improvement_pct, na.rm = TRUE),
    sd_improvement_pct = sd(improvement_pct, na.rm = TRUE),
    se_improvement_pct = sd_improvement_pct / sqrt(n_used),
    ci_low = mean_improvement_pct - 1.96 * se_improvement_pct,
    ci_high = mean_improvement_pct + 1.96 * se_improvement_pct,
    .groups = "drop"
  ) %>%
  mutate(
    solver = as.character(heuristic)
  ) %>%
  select(
    solver,
    n_used,
    mean_improvement_pct,
    sd_improvement_pct,
    se_improvement_pct,
    ci_low,
    ci_high
  )

ai_baseline <- tibble(
  solver = "AI",
  n_used = NA_integer_,
  mean_improvement_pct = 0,
  sd_improvement_pct = NA_real_,
  se_improvement_pct = NA_real_,
  ci_low = NA_real_,
  ci_high = NA_real_
)

overall_improvement_plot_table <- bind_rows(
  ai_baseline,
  overall_improvement_table
) %>%
  mutate(
    solver = factor(
      solver,
      levels = c("AI", heuristic_order)
    ),
    performance = case_when(
      mean_improvement_pct > 0 ~ "AI better",
      mean_improvement_pct < 0 ~ "AI worse",
      TRUE ~ "Baseline"
    ),
    label = paste0(round(mean_improvement_pct, 1), "%")
  )

View(overall_improvement_plot_table)


# ------------------------------------------------------------
# Solo mean barplot: no confidence intervals
# ------------------------------------------------------------

plot_overall_mean_bar <- ggplot(
  overall_improvement_plot_table,
  aes(
    x = solver,
    y = mean_improvement_pct,
    fill = performance
  )
) +
  geom_hline(
    yintercept = 0,
    linetype = "dashed",
    linewidth = 0.7,
    color = "grey35"
  ) +
  geom_col(
    width = 0.7,
    color = "white",
    linewidth = 0.3
  ) +
  geom_text(
    aes(label = label),
    vjust = ifelse(
      overall_improvement_plot_table$mean_improvement_pct >= 0,
      -0.4,
      1.2
    ),
    size = 3.5
  ) +
  scale_fill_manual(
    values = c(
      "AI better" = "#2166AC",
      "AI worse" = "#B2182B",
      "Baseline" = "grey70"
    )
  ) +
  labs(
    title = "Overall Mean AI Improvement over Heuristics",
    subtitle = "Positive values mean AI is better on average",
    x = "Solver / comparison heuristic",
    y = "Mean AI improvement (%)",
    fill = "Result"
  ) +
  theme_ai +
  theme(
    axis.text.x = element_text(angle = 30, hjust = 1)
  )

plot_overall_mean_bar


# ------------------------------------------------------------
# Solo CI plot: confidence intervals only
# ------------------------------------------------------------
# AI baseline is removed here because it has no CI.

overall_ci_plot_table <- overall_improvement_plot_table %>%
  filter(solver != "AI")

plot_overall_ci <- ggplot(
  overall_ci_plot_table,
  aes(
    x = solver,
    y = mean_improvement_pct,
    color = performance
  )
) +
  geom_hline(
    yintercept = 0,
    linetype = "dashed",
    linewidth = 0.7,
    color = "grey35"
  ) +
  geom_errorbar(
    aes(
      ymin = ci_low,
      ymax = ci_high
    ),
    width = 0.15,
    linewidth = 0.8,
    na.rm = TRUE
  ) +
  geom_point(
    size = 3,
    na.rm = TRUE
  ) +
  scale_color_manual(
    values = c(
      "AI better" = "#2166AC",
      "AI worse" = "#B2182B",
      "Baseline" = "grey70"
    )
  ) +
  labs(
    title = "Confidence Intervals for Overall Mean AI Improvement",
    subtitle = "Points show means; vertical lines show approximate 95% confidence intervals",
    x = "Comparison heuristic",
    y = "Mean AI improvement (%)",
    color = "Result"
  ) +
  theme_ai +
  theme(
    axis.text.x = element_text(angle = 30, hjust = 1)
  )

plot_overall_ci

# ------------------------------------------------------------
# CI plot by size and heuristic
# ------------------------------------------------------------
# CI is calculated for mean_improvement_pct within each size × heuristic.
# Positive values mean AI is better.
# Negative values mean AI is worse.

ci_by_size_heuristic <- big_table %>%
  group_by(size, heuristic) %>%
  summarise(
    n_used = sum(!is.na(improvement_pct)),
    mean_improvement_pct = mean(improvement_pct, na.rm = TRUE),
    sd_improvement_pct = sd(improvement_pct, na.rm = TRUE),
    se_improvement_pct = sd_improvement_pct / sqrt(n_used),
    
    # We use a t-based confidence interval instead of the normal 1.96 rule,
    # because the true standard deviation is unknown and estimated from a
    # relatively small number of runs per size/heuristic.
    # The t-distribution accounts for this extra uncertainty by making the
    # interval slightly wider when n is small.
    t_crit = qt(0.975, df = n_used - 1),
    ci_low = mean_improvement_pct - t_crit * se_improvement_pct,
    ci_high = mean_improvement_pct + t_crit * se_improvement_pct,
    
    .groups = "drop"
  ) %>%
  mutate(
    performance = case_when(
      mean_improvement_pct > 0 ~ "AI better",
      mean_improvement_pct < 0 ~ "AI worse",
      TRUE ~ "Tie"
    )
  )

View(ci_by_size_heuristic)


plot_ci_by_size <- ggplot(
  ci_by_size_heuristic,
  aes(
    x = heuristic,
    y = mean_improvement_pct,
    color = performance
  )
) +
  geom_hline(
    yintercept = 0,
    linetype = "dashed",
    linewidth = 0.7,
    color = "grey35"
  ) +
  geom_errorbar(
    aes(
      ymin = ci_low,
      ymax = ci_high
    ),
    width = 0.18,
    linewidth = 0.8,
    na.rm = TRUE
  ) +
  geom_point(
    size = 2.8,
    na.rm = TRUE
  ) +
  facet_wrap(~ size, scales = "free_y") +
  scale_color_manual(
    values = c(
      "AI better" = "#2166AC",
      "AI worse" = "#B2182B",
      "Tie" = "grey60"
    )
  ) +
  labs(
    title = "Confidence Intervals for Mean AI Improvement by Problem Size",
    subtitle = "Points show means; vertical lines show t-based 95% confidence intervals",
    x = "Heuristic",
    y = "Mean AI improvement (%)",
    color = "Result"
  ) +
  theme_ai

plot_ci_by_size
# ------------------------------------------------------------
#  Save all plots to WSL project folder
# ------------------------------------------------------------

plot_dir <- "./plots"

if (!dir.exists(plot_dir)) {
  dir.create(plot_dir, recursive = TRUE)
}

save_plot <- function(plot_object, filename, width = 10, height = 6) {
  ggsave(
    filename = file.path(plot_dir, filename),
    plot = plot_object,
    width = width,
    height = height,
    dpi = 300
  )
}

save_plot(plot_boxplot_improvement, "01_boxplot_ai_improvement.png", width = 12, height = 7)
save_plot(plot_line_mean_improvement, "02_line_mean_improvement.png", width = 10, height = 6)
save_plot(plot_heatmap_improvement, "03_heatmap_mean_improvement.png", width = 10, height = 6)
save_plot(plot_scatter_distance, "04_scatter_ai_vs_heuristic_distance.png", width = 12, height = 7)
save_plot(plot_difference_distance, "05_boxplot_absolute_distance_difference.png", width = 12, height = 7)
save_plot(plot_win_loss, "06_win_tie_loss_rate.png", width = 12, height = 7)
save_plot(plot_failure_rate, "07_failure_cutoff_rate.png", width = 10, height = 6)
save_plot(plot_overall_mean_bar, "08_overall_mean_barplot.png", width = 10, height = 6)
save_plot(plot_overall_ci, "09_overall_ci_plot.png", width = 10, height = 6)
save_plot(plot_ci_by_size, "10_ci_by_size_and_heuristic.png", width = 12, height = 7)

cat("Plots saved to:", normalizePath(plot_dir), "\n")