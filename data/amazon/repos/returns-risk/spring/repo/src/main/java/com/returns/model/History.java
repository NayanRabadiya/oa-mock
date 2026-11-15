package com.returns.model;

/** The approved returns of an account group in the last 90 days: how many, and how much was refunded. */
public record History(int count, double total) {}
