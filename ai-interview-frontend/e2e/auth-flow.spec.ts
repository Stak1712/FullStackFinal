import { expect, test } from "@playwright/test";

test("guest can register, open profile and logout", async ({ page }) => {
  const email = `e2e-${Date.now()}@example.com`;

  await page.goto("/register");
  await page.getByLabel("Имя").fill("Турпал");
  await page.getByLabel("Фамилия").fill("Шабазов");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Пароль").fill("password123");
  await page.getByRole("button", { name: "Создать аккаунт" }).click();

  await expect(page.getByRole("heading", { name: "Профиль" })).toBeVisible();
  await expect(page.getByText(email)).toBeVisible();

  await page.getByRole("button", { name: "Выйти" }).click();
  await expect(page.getByRole("heading", { name: "Вход" })).toBeVisible();
});
