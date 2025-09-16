import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import api, { setAccessToken } from "../api/axios";

type User = { id: number; username: string };
type State = { access: string | null; user: User | null; status: "idle"|"loading"|"error" };
const initial: State = { access: null, user: null, status: "idle" };

export const login = createAsyncThunk("auth/login",
  async (p: { username: string; password: string }) => {
    const { data } = await api.post("/login/", p);
    return data as { access: string; user: User };
  }
);

export const refresh = createAsyncThunk("auth/refresh",
  async () => {
    const { data } = await api.post("/refresh/", {});
    return data as { access: string };
  }
);

export const logout = createAsyncThunk("auth/logout",
  async () => { await api.post("/logout/", {}); }
);

const slice = createSlice({
  name: "auth",
  initialState: initial,
  reducers: {},
  extraReducers: (b) => {
    b.addCase(login.pending, (s) => { s.status = "loading"; });
    b.addCase(login.fulfilled, (s, a) => {
      s.status = "idle";
      s.access = a.payload.access;
      s.user = a.payload.user;
      setAccessToken(a.payload.access);
    });
    b.addCase(login.rejected, (s) => { s.status = "error"; });

    b.addCase(refresh.fulfilled, (s, a) => {
      s.access = a.payload.access;
      setAccessToken(a.payload.access);
    });

    b.addCase(logout.fulfilled, (s) => {
      s.access = null; s.user = null; setAccessToken(null);
    });
  },
});

export default slice.reducer;
