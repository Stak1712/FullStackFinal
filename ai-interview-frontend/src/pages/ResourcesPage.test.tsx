import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ResourcesPage from "./ResourcesPage";
import { fetchInterviewPrepResources } from "../api/resources";

vi.mock("../api/resources", () => ({
  fetchInterviewPrepResources: vi.fn(),
}));

const mockedFetch = vi.mocked(fetchInterviewPrepResources);

function renderPage() {
  return render(
    <MemoryRouter>
      <ResourcesPage />
    </MemoryRouter>
  );
}

describe("ResourcesPage", () => {
  beforeEach(() => mockedFetch.mockReset());

  it("loads interview preparation resources on mount", async () => {
    mockedFetch.mockResolvedValue({
      query: "FastAPI",
      source: "GitHub Search API",
      external_status: "live",
      items: [
        {
          title: "fastapi/interview",
          description: "Interview prep",
          url: "https://github.com/example/fastapi-interview",
          source: "GitHub",
          stars: 42,
          language: "Python",
          updated_at: "2026-05-12T00:00:00Z",
        },
      ],
    });

    renderPage();

    expect(await screen.findByText("fastapi/interview")).toBeInTheDocument();
    expect(mockedFetch).toHaveBeenCalledWith("FastAPI", 6);
  });

  it("shows fallback warning when external resources cannot be loaded", async () => {
    mockedFetch.mockResolvedValue({
      query: "FastAPI",
      source: "Fallback",
      external_status: "fallback",
      warning: "external api down",
      items: [],
    });

    renderPage();

    expect(await screen.findByText("external api down")).toBeInTheDocument();
    expect(await screen.findByText("Материалы по запросу не найдены.")).toBeInTheDocument();
  });

  it("submits a new skill query", async () => {
    mockedFetch.mockResolvedValue({ query: "React", source: "GitHub", external_status: "live", items: [] });
    const user = userEvent.setup();

    renderPage();
    await user.clear(screen.getByPlaceholderText("Например: FastAPI"));
    await user.type(screen.getByPlaceholderText("Например: FastAPI"), "React");
    await user.click(screen.getByRole("button", { name: /найти материалы/i }));

    await waitFor(() => expect(mockedFetch).toHaveBeenLastCalledWith("React", 6));
  });
});
