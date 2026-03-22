from physics_models.vertical_motion import VerticalMotion
from physics_models.inclined_plane import InclinedPlane

class ModelRouter:
    def execute_model(self, model_type: str, parameters: dict) -> dict:
        """
        Executa o modelo físico explicitamente solicitado pelo usuário.
        """
        g_val = parameters.get("gravity", 9.8)

        if model_type == "vertical_motion":
            modelo = VerticalMotion()
            return modelo.solve(
                y0_val=parameters.get("y0", 0),
                v0_val=parameters.get("v0", 0),
                g_val=g_val
            )
            
        elif model_type == "inclined_plane":
            modelo = InclinedPlane()
            return modelo.solve(
                mass_val=parameters.get("mass", 1),
                angle_deg_val=parameters.get("angle", 0),
                g_val=g_val
            )
            
        else:
            return {
                "error": True,
                "message": f"Modelo '{model_type}' não suportado ou inexistente."
            }