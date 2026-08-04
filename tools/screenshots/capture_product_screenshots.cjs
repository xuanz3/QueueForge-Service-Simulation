const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const root = process.cwd();
const output = path.join(root, "docs", "assets", "readme");
const baseUrl = process.env.QUEUEFORGE_SCREENSHOT_URL
  || "http://host.docker.internal:15177";

fs.rmSync(output, { recursive: true, force: true });
fs.mkdirSync(output, { recursive: true });

const screenshots = [
  "01-product-overview.png",
  "02-scenario-configuration.png",
  "03-live-run-lifecycle.png",
  "04-staffing-comparison.png",
  "05-analytics-json-output.png",
  "06-simulation-kpis.png",
  "07-simulation-json-output.png",
  "08-mobile-interface.png",
];

const pause = (milliseconds) =>
  new Promise((resolve) => setTimeout(resolve, milliseconds));

async function installStableVisuals(page) {
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation: none !important;
        transition: none !important;
        caret-color: transparent !important;
      }
      html { scroll-behavior: auto !important; }
    `,
  });
}

async function scrollTo(page, locator, offset = 100) {
  await locator.scrollIntoViewIfNeeded();
  await page.evaluate((amount) => window.scrollBy(0, -amount), offset);
  await pause(150);
}

async function pageScreenshot(page, name) {
  await page.screenshot({
    path: path.join(output, name),
    fullPage: false,
    animations: "disabled",
  });
}

async function elementScreenshot(locator, name) {
  await locator.screenshot({
    path: path.join(output, name),
    animations: "disabled",
  });
}

(async () => {
  const browser = await chromium.launch({ headless: true });

  try {
    const desktop = await browser.newContext({
      viewport: { width: 1440, height: 960 },
      deviceScaleFactor: 1,
      colorScheme: "light",
    });
    const page = await desktop.newPage();

    await page.goto(baseUrl, {
      waitUntil: "networkidle",
      timeout: 120000,
    });
    await page.locator(".connection.ready").waitFor({ timeout: 120000 });
    await installStableVisuals(page);

    await page.evaluate(() => window.scrollTo(0, 0));
    await pageScreenshot(page, screenshots[0]);

    const scenarioHeading = page.getByRole("heading", {
      name: "Scenario preset",
    });
    const scenarioPanel = scenarioHeading.locator(
      "xpath=ancestor::section[contains(@class,'panel')][1]"
    );
    await scrollTo(page, scenarioPanel, 90);
    await elementScreenshot(scenarioPanel, screenshots[1]);

    const runsInput = page
      .locator("label.field")
      .filter({ hasText: "Runs per option" })
      .locator("input");
    await runsInput.fill("20");

    const compareButton = page.getByRole("button", {
      name: "Compare staffing options",
    });
    await scrollTo(page, compareButton, 180);
    await compareButton.click();
    await page.locator(".run-card").waitFor({ timeout: 30000 });
    await pageScreenshot(page, screenshots[2]);

    const staffingHeading = page.getByRole("heading", {
      name: "Staffing comparison",
    });
    await staffingHeading.waitFor({ timeout: 120000 });
    await scrollTo(page, staffingHeading, 110);
    await pageScreenshot(page, screenshots[3]);

    const analyticsDetails = page.locator("details.raw-result").last();
    await analyticsDetails.locator("summary").click();
    await scrollTo(page, analyticsDetails, 90);
    await elementScreenshot(analyticsDetails, screenshots[4]);

    const simulationTab = page.getByRole("tab", {
      name: "Single simulation",
    });
    await scrollTo(page, simulationTab, 120);
    await simulationTab.click();

    const simulationButton = page.getByRole("button", {
      name: "Run simulation",
    });
    await scrollTo(page, simulationButton, 180);
    await simulationButton.click();

    const queueHeading = page.getByRole("heading", {
      name: "Queue outcome",
    });
    await queueHeading.waitFor({ timeout: 120000 });
    await scrollTo(page, queueHeading, 110);
    await pageScreenshot(page, screenshots[5]);

    const simulationDetails = page.locator("details.raw-result").last();
    await simulationDetails.locator("summary").click();
    await scrollTo(page, simulationDetails, 90);
    await elementScreenshot(simulationDetails, screenshots[6]);

    await desktop.close();

    const mobile = await browser.newContext({
      viewport: { width: 390, height: 844 },
      deviceScaleFactor: 1,
      isMobile: true,
      hasTouch: true,
      colorScheme: "light",
    });
    const mobilePage = await mobile.newPage();
    await mobilePage.goto(baseUrl, {
      waitUntil: "networkidle",
      timeout: 120000,
    });
    await mobilePage.locator(".connection.ready").waitFor({
      timeout: 120000,
    });
    await installStableVisuals(mobilePage);
    await mobilePage.evaluate(() => window.scrollTo(0, 0));
    await pageScreenshot(mobilePage, screenshots[7]);
    await mobile.close();
  } finally {
    await browser.close();
  }

  const files = fs
    .readdirSync(output)
    .filter((name) => name.endsWith(".png"))
    .sort();

  if (JSON.stringify(files) !== JSON.stringify(screenshots)) {
    throw new Error(
      `Expected exactly ${screenshots.length} screenshots, found: ${files.join(", ")}`
    );
  }

  console.log(`Captured ${files.length} QueueForge product screenshots.`);
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
