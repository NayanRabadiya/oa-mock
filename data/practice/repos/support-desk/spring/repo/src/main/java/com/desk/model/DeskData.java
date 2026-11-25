package com.desk.model;

import java.util.List;

/** A data set for the store: what src/main/resources/seed.json holds. */
public record DeskData(List<Agent> agents, List<Ticket> tickets) {}
