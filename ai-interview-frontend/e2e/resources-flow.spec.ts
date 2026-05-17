import { expect, test } from "@playwright/test";

test("resources page searches external interview preparation materials", async ({ page }) => {
  await page.goto("/resources");

  await expect(page.getByRole("heading", { name: "Материалы для подготовки к интервью" })).toBeVisible();
  await page.getByPlaceholder("Например: FastAPI").fill("Docker");
  await page.getByRole("button", { name: /Найти материалы|Ищу материалы/ }).click();

  await expect(page.getByText(/Результаты: Docker/)).toBeVisible();
  await expect(page.getByText(/Источник:/)).toBeVisible();
});
