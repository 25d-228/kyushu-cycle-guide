# Kyushu Cycle Journey

A Japanese-language cycling trip planner starting and ending in Orio, Kitakyushu.

## Website

Expected GitHub Pages address: https://25d-228.github.io/kyushu-cycle-guide/

A URL here is not proof that publishing has completed. Check the repository's Actions and Settings > Pages for deployment status.

## Features

- Four-day inland trial loop and fourteen-day Kyushu itinerary.
- Map comparison, day navigation, and previous/next-place navigation.
- Sightseeing suggestions and estimated visit times.
- Hotel information with links to Jalan listings.
- Full rest-day plans for Hita, Kumamoto, and Miyazaki.
- Departure dates and saved choices stored only in each browser.

## Running locally

Open `index.html` in a modern browser. The website is self-contained; no backend, API key, package installation, or build is needed.

## Publishing

This repository contains the latest navigator from the trip-planning conversation. The one-time import workflow verifies the original HTML checksum before writing `index.html`.

For branch-based publishing, select the branch containing `index.html` and `/(root)` under **Settings > Pages > Deploy from a branch**. `.nojekyll` disables Jekyll processing.

## Privacy and limitations

The website and itinerary are public when published. Do not commit booking references, private contact information, or a precise home address.

Saved selections and departure dates are local to the browser and are not synced between devices. Existing selections in a downloaded HTML file will not automatically transfer to the hosted site.

Routes are schematic planning lines, not verified cycling navigation or GPS positions. Distances, sightseeing durations, budgets, and rest-day schedules are estimates. Recheck road restrictions, opening hours, ferry schedules, hotel availability and bicycle-storage policies before travelling. Hotel links do not provide live prices or reservations.

Original third-party map-data attribution and source links are retained in the website.
