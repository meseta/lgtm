// matches /github_auth_flow/apps/utils/models.py
export interface UserData {
  profileImage: string;
  name: string;
  handle: string;
  id: string;
  accessToken: string;
}

export interface AuthState {
  uid: string | null;
  userData: UserData | null;
}

